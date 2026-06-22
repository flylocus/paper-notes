import json
import sys

def main():
    gd_path = 'outputs/ready/20260621/2606.19464/generate_data.json'
    ds_path = 'fused/2606.19464_deepseek_payload_patch_20260621.json'
    
    with open(gd_path, 'r', encoding='utf-8') as f:
        gd = json.load(f)
        
    with open(ds_path, 'r', encoding='utf-8') as f:
        ds = json.load(f)
        
    patch = ds.get('payload_patch', {})
    for k, v in patch.items():
        gd[k] = v
        
    with open(gd_path, 'w', encoding='utf-8') as f:
        json.dump(gd, f, indent=2, ensure_ascii=False)
        
    print("Merged patch successfully!")

if __name__ == '__main__':
    main()
