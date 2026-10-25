# Unit tests under each break

Run on the baseline with each patch applied. Four breaks pass the mocked suite; those are the ones only the harness can see.

```
01-charge-first-line-only: 1 failed, 9 passed
02-declined-marked-paid: 1 failed, 9 passed
03-order-lines-quantity-one: 10 passed
04-cart-not-cleared: 1 failed, 9 passed
05-add-again-no-increment: 1 failed, 9 passed
06-cart-total-ignores-quantity: 10 passed
07-paid-without-charge-id: 1 failed, 9 passed
08-orders-oldest-first: 10 passed
09-empty-cart-checks-out: 1 failed, 9 passed
10-payments-ledger-zero-amount: 10 passed
```
