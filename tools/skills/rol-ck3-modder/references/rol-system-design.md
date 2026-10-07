# RoL Interacting Systems

Read this when designing or implementing character growth, companions, persistent consequences, relic uses, inheritance, or cross-chain effects. The examples below are design options, not existing features or an instruction to implement them all. Confirm implementation status from `PROJECT.md` and code.

## Build a Consequence Loop

Connect a requested mechanic through: player choice -> durable result -> later event/option -> cost or payoff. For example, studying one relic can produce a navigation clue, unlock an option on another expedition, and create an obligation to the scholar who helped.

- Give each new state a producer and at least one consumer. If the feature only gives a generic buff, explain its intended role rather than inventing a larger system.
- Distinguish character experience, expedition progress, relic ownership, historical completion, and dynasty knowledge. Losing an artifact must not silently erase a completed expedition; inheriting a relic must not silently grant its discoverer's experience.
- Share producers/consumers through scripted effects/triggers/values instead of copying state logic into each regional chain.

## Traits and Personality

- A progression trait with research/exploration/negotiation tracks is one possible shape. Verify track syntax against installed vanilla/workshop examples before coding; do not invent XP interfaces or final archetypes without a working precedent.
- Reward meaningful actions, including useful partial outcomes; prevent reopening an event or repeating one cheap decision from farming XP.
- Use personality for choices, willingness and matching stress costs: honesty can favor disclosure, greed can favor bargaining, bravery can favor rescue. Several personalities should remain viable.
- Separate acquired expertise from personality; expeditions should not casually replace existing personality traits. Temporary experiences normally belong in modifiers, not permanent traits.
- Prefer track unlocks that offer alternate routes or recovery, with modest stat bonuses. Avoid requiring the progression trait merely to reach the original high-stat success target.

## Companions and Rivals

- Select suitable existing characters for scholars, guards, guides or sponsors where possible; record the selected participant for later consequences rather than selecting a different random person at payoff time.
- Check the body of vanilla availability triggers before using them on activity participants. In CK3 1.20, `is_available_adult` rejects `involved_activity` (and travel); it is unsuitable for an already attending companion. Require actual attendance separately from alive/adult/not imprisoned/not incapable checks. Revalidate both at selection and at the aid consumer; settlement may intentionally remain payable after departure.
- Event portraits, outcomes and saved scopes must refer to the same participant. Guard against dead/missing participants and changed ownership; choose a proportionate fallback or close the unresolved thread.
- Define cooperation terms and subsequent obligations: shared credit, payment, a court role, public recognition or access to research. Breaking terms can create opinion loss, a grievance or a follow-up event.
- Use cooldowns and bounded follow-ups. Prefer scoped on-actions/decisions/delayed events over frequent global character scans. Do not create recurring rival NPCs without a lifecycle.

## Evidence, Failure and Retry

- Partial success can yield a map, transcription, contact or clue that reduces cost, unlocks a route or grants one recovery opportunity on retry.
- Specify whether evidence is region-specific, expiring, consumed, transferable or reusable. Consume one-use evidence once at the relevant action, not on both event entry and option selection.
- Record which outcomes preserve useful progress and which end the expedition. Keep full completion/reward separate from evidence; avoid issuing the unique artifact on a partial path.
- Never insert a new compulsory failure roll without recalculating the intended complete route and updating exact tooltips. Use the existing roughly 70% high-stat target unless the user changes it.

## Buffs and Relic Uses

For each modifier, decide recipient (character/artifact/dynasty/county), source, duration, stacking, refresh/replacement, termination and feedback.

- Mutually exclusive relic uses can support combat, research, public display or navigation. Specify switching cost and any maintenance obligation; implement only uses within the requested scope.
- Grant artifact benefits to the intended owned artifact, not a random artifact. Revalidate ownership before an upgrade or delayed payoff.
- Snapshot the selected artifact on entry and reuse that pointer; a delayed event must not pick a replacement of the same type after the original changes owner. Offer a neutral invalid-project closure and clear its state.
- In native decisions, `minimum_cost` blocks unaffordable entry but does not charge. Put the actual fee in the committing decision's `cost`, or use an explicitly guarded payment effect once. Check additional paid event options against current funds. Installed `pam_saint_decisions.txt` documents the picker/commit distinction.
- Guard one-time rewards and fragment levels so repeated console/event calls do not duplicate artifacts or permanently stack the same benefit. Respect existing cooldowns and completion semantics.
- For expiring or conditional benefits, explain expiry/conditions to the player. Reuse opinion, stress, prestige and short-term modifiers where they express the actual consequence.

## Cross-Chain and Inheritance

- Earlier discoveries may unlock optional routes, cheaper preparation or limited recovery on another chain. Each original chain should remain independently completable; avoid circular prerequisite locks.
- Keep old four-chain Legend Circle and separate fivefold enhancement semantics intact unless explicitly redesigned.
- Decide what inheritance transfers: artifact, research notes, agreements, or obligations. Keep personal expertise separate from family knowledge and let successors respond to inherited duties.
- Handle old saves without new variables/flags; initialize when entering the feature rather than assuming historical events ran. Use stable existing IDs unless migration is part of the task.
- Verify callback timing from installed `common/on_action/death.txt`: in 1.20, `on_death` runs on the about-to-die character. Check that the predecessor is the player and the `player_heir` is alive; do not assume the heir already has `is_ai = no`. Gate the delayed recipient event after succession instead.
- For inherited obligations, snapshot the original participant/terms, merge distinct sources without replacing a recipient's personal pact, and retain unread sources through another succession. Keep inherited earned XP at zero. For delayed repeatable projects, capture a monotonically increasing generation in the event and match it before payout or cleanup; a pending flag alone does not distinguish an old event from a new job.

## Minimum Meaningful Verification

- Trace entry -> state creation -> later consumer -> cleanup, including failure and replay.
- Inspect scope type and participant/owner validity at each delayed event. Script shape checks cannot prove runtime scopes.
- A source model must not assume that an unfamiliar vanilla helper means what its name suggests. Verify the helper against installed source, model only the semantics needed, and record unsupported native behavior as a runtime uncertainty.
- For probabilistic changes, compare actual formula, caps and tooltip, and compute only meaningful route probabilities with explicit assumptions.
- Extend static contracts only when they can catch real broken wiring. Do not add wording-matching tests as a proxy for behavior.
- When game testing is left to the user, provide the new console/decision entry, expected state, reset instructions and the runtime uncertainty; do not launch CK3.
