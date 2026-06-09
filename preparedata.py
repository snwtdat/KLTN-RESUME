import json
import re

def process_data(input_file, output_file):
    print(f"1. Đang đọc dữ liệu gốc từ {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    dataset = []
    # MỞ KHÓA TOÀN BỘ 5 NHÃN
    valid_labels = ["SKILL", "JOB_TITLE", "EDUCATION", "EXPERIENCE", "CERTIFICATE"]
    
    print("2. Đang chuyển đổi tọa độ sang BIO...")
    for item in data:
        if 'annotations' not in item or len(item['annotations']) == 0:
            continue
            
        text = item['data']['text']
        results = item['annotations'][0].get('result', [])
        
        entities = []
        for r in results:
            if r.get('type') == 'labels':
                val = r['value']
                label_name = val['labels'][0]
                
                if label_name in valid_labels:
                    entities.append({
                        'start': val['start'],
                        'end': val['end'],
                        'label': label_name
                    })
        
        entities = sorted(entities, key=lambda x: x['start'])
        
        tokens = []
        ner_tags = []
        
        for match in re.finditer(r'\S+', text):
            word = match.group()
            start_char = match.start()
            end_char = match.end()
            
            tag = "O" 
            for ent in entities:
                if start_char >= ent['start'] and start_char < ent['end']:
                    if start_char == ent['start'] or (len(tokens) > 0 and ner_tags[-1] == 'O'):
                        tag = f"B-{ent['label']}"
                    else:
                        tag = f"I-{ent['label']}"
                    break
                    
            tokens.append(word)
            ner_tags.append(tag)
            
        dataset.append({
            "tokens": tokens,
            "ner_tags": ner_tags
        })
        
    print("3. Đang đóng gói dữ liệu...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
        
    print(f"=> HOÀN TẤT! Đã đóng gói xong {len(dataset)} CV vào file: {output_file}")

if __name__ == "__main__":
    process_data('test17.json', 'biotest17.json')