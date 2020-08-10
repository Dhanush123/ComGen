-- Google BigQuery query used on GitHub Archive dataset
SELECT repo.name, JSON_EXTRACT_SCALAR(payload, '$.pull_request.base.repo.archive_url') as archive_url, MAX(CAST(JSON_EXTRACT_SCALAR(payload, '$.pull_request.base.repo.stargazers_count') AS INT64)) AS stars
FROM `githubarchive.month.202006`
WHERE JSON_EXTRACT_SCALAR(payload, '$.pull_request.head.repo.language') = 'Python'
GROUP by repo.name, archive_url
ORDER BY stars DESC