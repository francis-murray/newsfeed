# Evaluation of Efficiency and Correctness

## Efficiency Evaluation

To evaluate efficiency, I would measure and collect the execution time or latency of each major component in the system, including:

- Fetching data from external sources  
- Filtering 
- Relevance scoring  
- Reading from and writing to disk or the database  
- Response times of the API endpoints

In addition to timing, I would track throughput. For example, I would monitor how many news items are ingested per second to ensure the system can handle high-volume batches efficiently.

I would then visualize all the metrics on a web dashboard, using time series charts to show performance trends over time. I would also compute and display the average, minimum, and maximum times for each operation, and set up alerts to trigger when performance metrics exceed defined thresholds. This setup would help identify bottlenecks and ensure the system remains responsive under peak workloads.

Another way to analyze efficiency would be to profile the system using a profiling tool. This would make it possible to examine performance at the function level and optimize any slow sections of the code.

## Correctness
To evaluate the correctness of the app's filtering process, I would use standard information retrieval metrics: **Precision** and **Recall**.

In this context:

- **Recall** measures how many of the relevant items were successfully retrieved.
    - Formula: Recall = TP / (TP + FN)

- **Precision** measures how many of the retrieved items are actually relevant.
    - Formula: Precision = TP / (TP + FP)

Where:
- TP = true positives (relevant items correctly identified)
- FP = false positives (irrelevant items incorrectly identified as relevant)
- FN = false negatives (relevant items missed by the system)

In the context of our news retrieval app:

- A low recall means we are **missing relevant news** in our results. This is something we definitely want to avoid, as we might be missing out on important news.
- A low precision means we are **getting some irrelevant news** in our results. This can clutter our results, but might be less critical, especially if we have a good ranking algorithm, which would push less relevant results to the bottom or further pages. 

Since missing critical news is worse than including a few irrelevant ones, recall is more important in our case. I would therefore pay close attention to this metric.

If we however wanted to keep track of both Precision and Recall using a single metric, we could use the **F1 score** = 2 × (Precision × Recall) / (Precision + Recall).

Finally, we could visualize the filtering performance using a **confusion matrix**, which would show the counts of true positives, false positives, false negatives, and true negatives for each test batch.