import csv, os

def save_ratings(b_rating, r_rating, m_rating, c_rating, out_file="ratings.csv"):
    file_exists = os.path.isfile(out_file)
    with open(out_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Baseline","RAG","MapReduce","Chaining"])
        writer.writerow([b_rating,r_rating,m_rating,c_rating])


def save_ratings_dict(ratings: dict, out_file="ratings.csv"):
    import csv, os
    file_exists = os.path.isfile(out_file)
    existing_header = None
    if file_exists:
        try:
            with open(out_file, "r", newline="") as f:
                for row in csv.reader(f):
                    if row and any(cell.strip() for cell in row):
                        existing_header = row
                        break
        except Exception:
            existing_header = None
    header = list(ratings.keys())
    need_header = (not file_exists) or (existing_header != header)
    with open(out_file, "a", newline="") as f:
        w = csv.writer(f)
        if need_header:
            w.writerow(header)
        w.writerow([ratings[k] for k in header])
