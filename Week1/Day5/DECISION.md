* **Gate Outputs**:

  * A

    * ruff check .
      All checks passed!
    * mypy .
      Success: no issues found in 2 source files
    * pytest -q
      .....                                                                                                                                                               [100%]5 passed in 0.01s
  * B

    * ruff check .
      All checks passed!
    * mypy .
      Success: no issues found in 2 source files
    * pytest -q
      ...F.                                                                                                                                                               [100%]1 failed, 4 passed in 0.10s
  * C

    * ruff check .
      All checks passed!
    * mypy .
      Success: no issues found in 2 source files
    * pytest -q
      ....F                                                                                                                                                               [100%]1 failed, 4 passed in 0.13s
* **Version Chosen for Production**

  * A
* **Why**

  * All of the rules tested have passed their pytest unit tests. Ruff, Mypy tests have also passed.
    * All arithmetic is exact. A binary float anywhere in the calculation is a defect.
    * `matched` is `True` **only** on an exact zero variance. There is no tolerance. A
      one-penny discrepancy is a discrepancy.
    * Empty statements have a variance == -expected_total and matched == False, unless `expected_total` is `"0.00"`, in which case `matched` is `True`.
    * `variance` is always quantised to two decimal places.
  * The extra two tests added to check exactness of the calculations and zero variance also passed for this version.
* **Rejected**

  * | Version | Rule Broken                                                                                                                         | Tests (refer to code below for test and outputs) | Consequence                                                                                             |
    | ------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
    | B       | All arithmetic is exact. A binary float anywhere in the calculation is a defect.                                                    | 1                                                | May have lost money in calculations, or created money that never existed.                               |
    | B       | `variance is always quantised to two decimal places.`                                                                             | 1                                                | Can lead to problems in production as we can not represent a fraction of a penny.                       |
    | C       | `matched` is `True` **only** on an exact zero variance. There is no tolerance. A one-penny discrepancy is a discrepancy. | 2                                                | Can lead to issues such as money going missing or being created as we scale the number of transactions. |
    ```python

    # 1
    def test_exact_match() -> None:
        result = reconcile(["0.10","0.20"],"0.30")
        assert result.matched is True
        assert result.variance == Decimal("0.00")

    """
    E       AssertionError: assert False is True
    E        +  where False = Reconciliation(variance=Decimal('4E-17'), matched=False).matched

    tests/test_reconcile.py:27: AssertionError
    """

    # 2
    def test_many_lines_with_discrepancy() -> None:
        lines = ["25.01", "25.00", "25.00", "25.00"]
        result = reconcile(lines, "100.00")
        assert result.variance == Decimal("0.01")
        assert result.matched is False
    """
    E       AssertionError: assert True is False
    E        +  where True = Reconciliation(variance=Decimal('0.01'), matched=True).matched

    tests/test_reconcile.py:35: AssertionError

    """
    ```
