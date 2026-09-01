#!/bin/bash
curl -X POST "https://api.indexnow.org/indexnow" \
     -H "Content-Type: application/json" \
     -d '{
  "host": "offline-automations.online",
  "key": "39c54f9ef36247ad89ce28006318c488",
  "keyLocation": "https://offline-automations.online/39c54f9ef36247ad89ce28006318c488.txt",
  "urlList": [
    "https://offline-automations.online/",
    "https://offline-automations.online/products/",
    "https://offline-automations.online/products/hybrid-verification/",
    "https://offline-automations.online/products/semantic-mapping/",
    "https://offline-automations.online/products/local-security/",
    "https://offline-automations.online/blog/",
    "https://offline-automations.online/blog/semantic-chaos-in-accounting/",
    "https://offline-automations.online/blog/daily-fresh-report-vs-monthly-rush/",
    "https://offline-automations.online/blog/local-llm-architecture-for-enterprise/",
    "https://offline-automations.online/about/",
    "https://offline-automations.online/contact/"
  ]
}'
