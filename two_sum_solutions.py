"""
Способ a (brute force): O(n^2), два вложенных цикла.
Способ b (hashmap): O(n), один проход, хранение в dict.

HashMap выигрывает за счёт линейного времени
"""

def two_sum_brute_force(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


def two_sum_hashmap(nums, target):
    seen = {}  # значение -> индекс
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []


if __name__ == "__main__":
    nums = [2, 7, 11, 15]
    target = 9
    print("Brute force:", two_sum_brute_force(nums, target))
    print("Hashmap:", two_sum_hashmap(nums, target))

"""
На типовых тестах LeetCode решение в лоб либо TLE, либо показывает заметно большее время (сотни миллисекунд и выше).
Решение через HashMap стабильно Accepted на всех тестах.
"""
