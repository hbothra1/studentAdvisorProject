from collections import Counter

def get_top_course_counts_across_rankings(rankings, top_k=10):
    """
    Count how many times each course appears in the top K of any ranking category.

    Args:
        rankings (dict): Output from match_jd_to_courses(). rankings should be a dictionary, keys are categories and values are lists of tuples (course_code, score). East list should be sorted by score (descending) 
        top_k (int): Number of top courses to consider in each category.

    Returns:
        Counter: A dictionary-like object mapping course codes to frequency counts.
    """
    composite_ranking = Counter()

    for category, ranked_list in rankings.items():
        for course_code, _ in ranked_list[:top_k]:
            composite_ranking[course_code] += 1

    return composite_ranking

def get_unique_courses_in_top_rankings(rankings, top_k=10):
    """
    Get a list of all unique courses that appear in the top K rankings across all categories.

    Args:
        rankings (dict): Output from match_jd_to_courses(). Rankings should be a dictionary where keys are categories
                         and values are lists of tuples (course_code, score), sorted by score (descending).
        top_k (int): Number of top courses to consider in each category.

    Returns:
        list: A list of unique course codes that appear in the top K rankings across all categories.
    """
    shortlisted_courses = set()

    for category, ranked_list in rankings.items():
        # Add the top K courses from the current category to the set
        shortlisted_courses.update(course_code for course_code, _ in ranked_list[:top_k])

    return list(shortlisted_courses)

def get_courses_in_all_categories(rankings, top_k=10):
    """
    Get a list of course codes that appear in the top K rankings across all categories.

    Args:
        rankings (dict): Output from match_jd_to_courses(). Rankings should be a dictionary where keys are categories
                         and values are lists of tuples (course_code, score), sorted by score (descending).
        top_k (int): Number of top courses to consider in each category.

    Returns:
        list: A list of course codes that appear in the top K rankings of every category.
    """
    # Start with the set of courses in the first category
    common_courses = set(course_code for course_code, _ in rankings[next(iter(rankings))][:top_k])

    # Intersect with the courses in the top K of each subsequent category
    for category, ranked_list in rankings.items():
        category_courses = set(course_code for course_code, _ in ranked_list[:top_k])
        common_courses.intersection_update(category_courses)

    return list(common_courses)

