# backend/app/services/leetcode/queries.py

# Get problem list with specific difficulty and tags
LEETCODE_PROBLEM_LIST_QUERY = """
query problemsetQuestionListV2($categorySlug: String, $limit: Int, $filters: QuestionFilterInput) {
  problemsetQuestionListV2(categorySlug: $categorySlug, limit: $limit, filters: $filters) {
    questions {
      questionFrontendId
      title
      titleSlug
      difficulty
      paidOnly
    }
  }
}
"""

# Check whether a LeetCode account with the given username exists
LEETCODE_USER_PROFILE_QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
  }
}
"""

# Get the number of problems a user has solved, grouped by difficulty
LEETCODE_USER_SOLVED_STATS_QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
  }
}
"""
