# Storefront demo: hidden breaks and answers

Companion to [verification-framework-storefront-example](https://github.com/kennymatsudo/verification-framework-storefront-example). It was kept private until the demo was graded, and nothing in it was ever copied into the agent's workspace. It holds what the demo needs to grade the agent's work without the agent seeing it:

- `breaks/*.patch`: deliberate bugs against the storefront's baseline commit, one behavior each. After the agent builds checks, each patch is applied to a scratch worktree and the agent's checks are run through the harness. A break the checks do not catch is a check that would pass on broken code.
- `answers.json`: the developer's answers to the questions the skills ask, so a headless run of the demo gets the same answers every time. The answers never mention a break.
- `grade.py`: applies each break to a scratch clone of the example repo, starts the app through its harness, runs every check with `vf.py verify`, and reports which breaks a check read as Failed. It calls the harness's own tools, so it needs a checkout of the example repo with the harness in it.
- `unit-test-results.md`: which breaks the shop's own mocked unit tests catch. Four of the ten pass that suite; those are the ones only the harness can see.
- `results/`: one file per grading run, with the tally and each check's result lines.

The grading on 25 October 2026 caught nine of ten breaks at the example repo's commit `5409c15` (`09dd5d0` before its author was corrected). The miss, `08-orders-oldest-first`, is in the Orders feature, which was outside the scope the developer agreed to when the checks were built, so no check reads the orders page. To rerun it:

```sh
git clone https://github.com/kennymatsudo/verification-framework-storefront-example ../storefront
python3 grade.py ../storefront            # or --commit <sha>, --only 03,07
```

## Breaks

| Patch | Requirement | What a user would notice |
| --- | --- | --- |
| 01-charge-first-line-only | CO-2 | The card is charged for the first item only; the order says paid in full |
| 02-declined-marked-paid | CO-2, CO-3 | A declined card still produces a paid order |
| 03-order-lines-quantity-one | CO-1 | Every stored line says quantity 1 whatever the customer ordered |
| 04-cart-not-cleared | CO-4 | The cart still holds the items after paying |
| 05-add-again-no-increment | CT-1 | Adding an item twice leaves one in the cart |
| 06-cart-total-ignores-quantity | CT-3 | The cart page's total ignores quantities; storage is right |
| 07-paid-without-charge-id | CO-2 | The order is paid but records no payment ID |
| 08-orders-oldest-first | OR-1 | The orders page lists oldest first |
| 09-empty-cart-checks-out | CO-5 | Paying with an empty cart creates an empty paid order |
| 10-payments-ledger-zero-amount | CO-2 | The payments service answers with the right amount but records zero in its ledger |

Which of these the shop's own mocked unit tests catch is recorded in `unit-test-results.md`. The point of the demo is the ones they don't.
