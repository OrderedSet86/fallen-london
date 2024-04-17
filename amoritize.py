def amoritizedActions(percent, incr, brkpoint=100, compr=lambda a, b: a >= b):
    cost = 0
    overall_fail_probability = 1
    while True:
        added_cost = max(1-percent/100, 0)
        overall_fail_probability *= added_cost
        print(f'Costs {added_cost}')
        cost += added_cost
        if compr(percent, brkpoint):
            break
        percent += incr
    return 1 + cost, 1-overall_fail_probability

# print(amoritizedActions(50, -10, 20, lambda a, b: a <= b))
# print(amoritizedActions(50, 5))
print(amoritizedActions(83, 5))
print(amoritizedActions(100, 0))
