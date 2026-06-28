import random

COUNT = 32
MIN_VAL = -500
MAX_VAL = 500

def format_triplet(triplet):
    first = True
    total = 0
    line = ""
    for (i, num) in triplet:
        total += num
        if not first:
            line += "\t + "
        line += f"[{i:2d}]:{num:4d}"
        first = False
    line += f" = {total:<4d}"
    return line, total

def print_triplets(nums):
    count = len(nums)
    count_triplets = 0
    for i in range(count):
        for j in range(i+1, count):
            for k in range(j+1, count):
                if nums[i] + nums[j] + nums[k] == 0:
                    triplet = [(i, nums[i]), (j, nums[j]), (k, nums[k])]
                    line, _ = format_triplet(triplet)
                    print(line)
                    count_triplets += 1
    return count_triplets

if __name__ == "__main__":
    nums = []
    for i in range(COUNT):
        nums.append(random.randint(MIN_VAL, MAX_VAL))

    print(nums)
    print("---- Triplets ----")
    print_triplets(nums)
