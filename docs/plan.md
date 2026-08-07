# Project Plan

High-level plan for the Strawberry Music Festival lost-and-found system. This is a
living document — it covers *what* we are building and *why*, not how. Implementation
details are deliberately out of scope.

**Status:** direction agreed, data model and lifecycle not yet designed.

---

## Purpose

The festival runs a lost-and-found operation. Items are turned in at a booth and
recorded on paper "Found Article Forms" kept in a binder. When a festival-goer later
calls the office describing something they lost, staff have to search that binder — or
a spreadsheet transcribed from it — by hand.

The system replaces that with a searchable record of everything in custody, and lets
staff find likely matches from a natural-language description given over the phone.

---

## The reframe

The existing implementation is "forms → spreadsheet." That is not what we are building.

> The system maintains a set of physical objects in custody, each with an AI-authored
> description built from whatever evidence exists. Matching is comparing descriptions
> to descriptions.

The important consequence: **a lost report and a found item are the same shape.** Both
are a description of a physical object, plus when and where, plus a person attached.
A caller saying "I lost a blue Patagonia fleece near the main stage on Saturday" is
producing the same kind of record as a volunteer photographing a fleece at the booth.
The only difference is which side of the match it sits on.

That symmetry gives one engine running both directions:

- **Caller describes → search the found inventory.** The primary use case.
- **Item turned in → search open lost reports → notify the owner.** Higher value, and
  nearly free if the model is symmetric. Not free at all if extraction and search are
  built as separate features.

Intake modality — paper form, booth photo, staff typing — produces evidence. It must
not drive the schema. This is the main flaw in the current design: `FoundItem` is
shaped like the paper form, so the form's limitations become the system's limitations.

---

## Core concepts

| Concept | Description |
|---|---|
| **Event** | Spring 2026, Fall 2026. Everything partitions by it. Already on the paper form. |
| **Item** | A physical object in custody. Moves through a lifecycle from received to returned or disposed. |
| **Report** | Someone says they lost something. A description plus a person. |
| **Evidence** | A photo, a scanned form, a staff note, a call transcript. Attaches to an Item *or* a Report; many per record. |
| **Match** | A proposed or confirmed link between a Report and an Item, carrying a score, the model's reasoning, and who confirmed it. |

**People and their contact details are their own concept**, not fields on an Item. A
Report can be authored by staff transcribing a phone call, or later by a member of the
public through a self-service form — same object, different author. Getting this right
now makes the public claim form a new front door onto existing machinery rather than a
rebuild.

---

## Principles

**Evidence is immutable; everything derived is recomputable.**
Store the original photo and the raw model output permanently. Descriptions,
attributes, categories, and any future embeddings are *derivations* that can be
regenerated. Models and prompts will change repeatedly, and reprocessing history must
stay possible. Cheap to establish now, painful to retrofit.

**The model authors the record; it does not fill in blanks.**
Rather than extracting a fixed set of fields, the model writes a rich canonical
description plus the structured attributes it is confident about. Illegible handwriting
should produce recorded *uncertainty*, never a confidently wrong value.

**The system proposes, staff decide.**
Ranked candidates with reasoning. Never an automatic release — a person signs for
handing an object to another person.

**Google Sheets is an export, not the system of record.**

---

## Decided constraints

These were settled in discussion and drive most of the design.

### Scale: under ~200 items per festival

Roughly 400 records/year; a couple thousand after five years. A single event's inventory
is on the order of 20k tokens of description.

**Therefore semantic search needs no retrieval infrastructure.** Filter to the event,
hand the model the full candidate set alongside the caller's description, get back a
ranked shortlist with per-candidate reasoning. It is a prompt, not a subsystem — and it
outperforms embedding search at this scale, because the model can reason that "puffy
coat" and "insulated jacket" are the same object rather than merely measuring distance.
With prompt caching on the inventory block, a lookup costs cents.

Explicitly **out of scope**: vector database, embedding pipeline, chunking, hybrid
search, retrieval tuning. Revisit only if volume grows by an order of magnitude.

The database is now a boring choice. Pick it for hosting, backups, and sync
convenience — not for vector support.

### Booth connectivity: unreliable, offline required

The defining engineering constraint. It rules out Streamlit for the booth surface,
which needs a live connection for every interaction and is poor on a phone.

With no signal at the booth, no model call can happen at capture time. Capture is
therefore:

> photograph item → a few taps of structured input → optional voice note → queue
> locally → sync when back in range → AI authors the description server-side

This is the evidence/derivation split as a hard requirement rather than a preference.
The constraint and the principle agree, which suggests the design is sound.

**Booth capture must be append-only.** Devices generate their own IDs; records are added
and never edited in the field. Sync then reduces to "upload the queue" — no merge
conflicts, no distributed-state problem. Allowing offline edits to existing records
would mean signing up for conflict resolution, so preserving this property is worth
real discipline.

### Users: staff now, public later

Build staff-only. Keep the public claim form as a known future surface (see People
above) and avoid choices that foreclose it.

---

## Surfaces

One backend spine, two surfaces with genuinely different requirements.

| | Office / query | Booth capture |
|---|---|---|
| Device | Desktop | Phone |
| Network | Assumed online | Assumed offline |
| Interaction | Read and judge | Append only |
| AI runs | At query time | After sync |

Since a real web frontend is needed for the booth regardless, both surfaces likely
share one stack rather than retaining Streamlit for the office. Decision deferred.

---

## Phasing

1. **Foundation** — event / item / report / evidence / match, storage, and the
   derivation pipeline.
2. **Office matching + paper backfill** — one phase, because backfilling the forms is
   how the inventory gets populated for searching. Delivers the phone-call use case.
3. **Booth capture** — offline-first mobile. The hard one.
4. **Proactive matching + public claim form** — new items auto-check open reports;
   customers submit their own descriptions.

---

## Risks

- **iOS PWA limitations.** If booth staff use iPhones, Safari lacks background sync
  support and cached storage can be evicted after a period of disuse. Queued photos
  sitting on a phone for two days is a plausible data-loss path. Must be verified
  before phase 3 — the main factor that would push toward a native app.
- **On-device photo storage.** Hundreds of multi-megabyte photos against browser
  storage quotas. Compression at capture will matter.
- **PII retention.** Names, addresses, phone numbers, and emails of festival-goers held
  across years. Warrants a deliberate retention policy before a public surface exists.
- **Model cost and latency are non-issues** at this scale. Do not optimize for them.

---

## Open questions

- **Item lifecycle.** The states an object moves through from turned-in to returned or
  donated, including end-of-festival disposition of unclaimed items. This is the next
  thing to pin down — the data model has to support it, and it likely has
  festival-specific quirks.
- Which surfaces share a stack, and what that stack is.
- Whether the paper Found Article Form survives once booth capture exists.

---

## Notes on the existing implementation

The current Streamlit app is expected to be largely replaced. Issues found during
review, recorded so they are not silently reintroduced:

- `is_valid_form`'s schema description is inverted relative to the prompt — the field
  says "True if the image was *not* a Found Item form," the prompt says the opposite.
- `matched_with_lost_item` and `returned_to_owner` have identical descriptions and can
  never disagree. The form distinguishes them: *Belongs To* filled means matched;
  *Released by* signed means returned.
- The schema drops fields the paper form carries: **When Found**, festival/year, the
  received-by and released-by staff entries, and the item drawing.
- `process_images_concurrently` uses an unbounded `asyncio.gather`; `CLAUDE.md`
  documents it as semaphore-bounded.
- `generate_img_zip` always writes JPEG but the uploader accepts PNG and WebP; an RGBA
  image raises on save.
- `to_dataframe` emits an `Is Valid Form` column that the empty-case `COLUMNS` constant
  omits.
- `LostItem` is a stub containing only `is_valid_form`.
- `tests/services/test_data_service.py` is empty; `process_images_concurrently` is
  untested.
- `found-1.jpg` and `found-2.jpg` are byte-identical duplicates (~2.5 MB of redundant
  binary in git).
- Eleven `.pyc` files are tracked in git despite `.gitignore` now covering
  `__pycache__`.
- `GEMINI_MODEL` defaults to `gemini-3.5-flash`; the identifier should be verified
  against the current model list.
