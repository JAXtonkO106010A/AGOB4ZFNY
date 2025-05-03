# Week 8: Data Quality Check and Conditional Routing with AWS Glue

## Overview
This week’s task was focused on implementing **data quality checks**, **conditional transformations**, and **routing** outcomes to different S3 paths (passed vs failed) using **AWS Glue ETL jobs**. The pipeline helps ensure only valid data proceeds forward while segregating invalid data for analysis.

---

## Key Components Implemented

### 1. **Glue ETL Job: aca-panel-QC-Lok**
- Performs the full ETL logic with conditional routing.
- Steps:
  - Loads input data (Load `min performance`).
  - Applies `Data Quality Check` node.
  - Adds evaluation and routing logic:
    - If quality passes → changes schema → loads to `Passed` S3 path.
    - If quality fails → changes schema → loads to `Failed` S3 path.

📸 **Image 1**: `image1.png` – Visual layout of the full Glue ETL job, showing quality branching logic and targets.
<img width="959" alt="image1" src="https://github.com/user-attachments/assets/b1bb7d60-2b14-46ea-8574-6f682c7f3f3b" />

---

### 2. **S3 Output - Failed Quality Data**
- Invalid data output is stored in:  
  `s3://academics-trf-lok/academics/faculty-performance/Quality Check/Failed/`

📸 **Image 2**: `image2.png` – Contents of the Failed folder with one file uploaded (175 bytes).
<img width="959" alt="image2" src="https://github.com/user-attachments/assets/b18248c2-810d-4176-97af-dcfef68ed355" />

---

### 3. **S3 Output - Passed Quality Data**
- Valid/cleaned records are stored in:  
  `s3://academics-trf-lok/academics/faculty-performance/Quality Check/Passed/`

📸 **Image 3**: `image3.png` – Contents of the Passed folder with output file (~3.2 KB).
<img width="959" alt="image3" src="https://github.com/user-attachments/assets/538a6157-831c-4309-8352-9de121d73beb" />

---

## GitHub Directory Structure Suggestion
```bash
week-08-quality-check-routing/
├── readme.md                # Documentation (this file)
├── images/
│   ├── image1.png           # Glue ETL visual job
│   ├── image2.png           # S3 Failed output
│   └── image3.png           # S3 Passed output
├── scripts/
│   └── glue_job_script.py   # (Optional) Glue script backup
```

---

## Summary
In Week 8, you built a complete end-to-end data quality validation pipeline using AWS Glue. The success and failure records were successfully routed and stored separately for audit and clean processing.

✅ **Best Practice Implemented:**  
- Modular Glue job with quality filters and routing.
- Good S3 directory hygiene for output separation.
- Scalable for additional validations.

Let me know if you want a ZIP-ready folder structure or markdown export!
