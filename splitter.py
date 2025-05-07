import os

# split_csv_by_size_with_folder.py

INPUT_FILE = "amsterdam_addresses.csv"  # the large CSV to split
MAX_BYTES = 20 * 1024 * 1024            # 20 MiB max per file
OUTPUT_DIR = "splits"                   # folder to hold all parts

def split_csv(input_path, max_bytes, output_dir):
    # Create output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_path, "r", encoding="utf-8-sig") as src:
        header = src.readline()
        part = 1
        chunk_bytes = len(header.encode("utf-8"))
        
        # Open first output file
        out_path = os.path.join(output_dir, f"part_{part}.csv")
        out = open(out_path, "w", encoding="utf-8-sig")
        out.write(header)
        
        for line in src:
            b = len(line.encode("utf-8"))
            # start new part if adding this line would exceed max_bytes
            if chunk_bytes + b > max_bytes:
                out.close()
                part += 1
                chunk_bytes = len(header.encode("utf-8"))
                out_path = os.path.join(output_dir, f"part_{part}.csv")
                out = open(out_path, "w", encoding="utf-8-sig")
                out.write(header)
            
            out.write(line)
            chunk_bytes += b
        
        out.close()
    
    print(f"Split into {part} files in '{output_dir}/' (each ≤ {max_bytes/(1024*1024):.0f} MiB).")

if __name__ == "__main__":
    split_csv(INPUT_FILE, MAX_BYTES, OUTPUT_DIR)