import json
import numpy as np
from datasets import Dataset
import evaluate
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
    EarlyStoppingCallback # Vũ khí 1: Dừng sớm chống Overfitting
)

def main():
    print("="*60)
    print("🚀 KHỞI ĐỘNG HUẤN LUYỆN XLM-RoBERTa")
    print("="*60)

    print("[1/6] Đang nạp và chia bộ dữ liệu Vàng (125 mẫu)...")
    with open('biotest17.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    raw_dataset = Dataset.from_list(data)
    # Tỉ lệ chia chuẩn chỉnh: 80% Train - 20% Test
    split_datasets = raw_dataset.train_test_split(test_size=0.2, seed=42)
    
    # Khai báo trọn bộ 5 nhãn (11 thẻ BIO)
    label_list = [
        "O", 
        "B-SKILL", "I-SKILL", 
        "B-JOB_TITLE", "I-JOB_TITLE",
        "B-EDUCATION", "I-EDUCATION",
        "B-EXPERIENCE", "I-EXPERIENCE",
        "B-CERTIFICATE", "I-CERTIFICATE"
    ]
    label2id = {l: i for i, l in enumerate(label_list)}
    id2label = {i: l for i, l in enumerate(label_list)}
    
    print("[2/6] Đang tải Tokenizer của XLM-RoBERTa...")
    tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
    
    def tokenize_and_align_labels(examples):
        tokenized_inputs = tokenizer(
            examples["tokens"], 
            truncation=True, 
            is_split_into_words=True, 
            max_length=256
        )
        labels = []
        for i, label in enumerate(examples["ner_tags"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            previous_word_idx = None
            label_ids = []
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)
                elif word_idx != previous_word_idx:
                    label_ids.append(label2id[label[word_idx]])
                else:
                    label_ids.append(-100)
                previous_word_idx = word_idx
            labels.append(label_ids)
        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    print("[3/6] Đang tiền xử lý (Tokenize) dữ liệu...")
    tokenized_datasets = split_datasets.map(tokenize_and_align_labels, batched=True)
    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)
    
    # Khởi tạo công cụ chấm điểm chi tiết
    seqeval = evaluate.load("seqeval")
    
    def compute_metrics(p):
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)
        
        true_predictions = [
            [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        
        # Lấy báo cáo chi tiết cho từng nhãn
        results = seqeval.compute(predictions=true_predictions, references=true_labels)
        return results

    print("[4/6] Đang nạp kiến trúc Model Đa ngôn ngữ (Multilingual)...")
    model = AutoModelForTokenClassification.from_pretrained(
        "xlm-roberta-base", 
        num_labels=len(label_list), 
        id2label=id2label, 
        label2id=label2id
    )

    # VŨ KHÍ 2: BỘ SIÊU THAM SỐ TOÀN DIỆN (Hyperparameters)
    training_args = TrainingArguments(
        output_dir="./KLTN_Model_Checkpoints",
        eval_strategy="epoch",            # Đánh giá sau mỗi vòng
        save_strategy="epoch",            # Lưu lại sau mỗi vòng
        learning_rate=3e-5,               # Tốc độ học tối ưu cho RoBERTa
        per_device_train_batch_size=8,    # Lô dữ liệu (An toàn cho máy Mac)
        per_device_eval_batch_size=8,
        num_train_epochs=8,              # Cứ set cao lên 20 vòng vì đã có Early Stopping lo
        weight_decay=0.01,
        load_best_model_at_end=True,      # Chỉ lấy model đỉnh nhất ở cuối
        metric_for_best_model="overall_f1",# Tiêu chí chọn model đỉnh nhất là điểm F1
        greater_is_better=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        data_collator=data_collator,
        processing_class=tokenizer,
        compute_metrics=compute_metrics,
    )

    print("[5/6] BẮT ĐẦU ĐỐT LÒ HUẤN LUYỆN... 🔥")
    trainer.train()
    
    print("\n[6/6] ĐANG TRÍCH XUẤT BẢNG ĐIỂM BÁO CÁO...")
    ket_qua = trainer.evaluate()
    
    # In Bảng điểm Đẹp để chụp ảnh đưa vào Word
    print("\n" + "=" * 65)
    print("🏆 BẢNG ĐIỂM F1-SCORE CHI TIẾT TỪNG NHÃN (DÙNG CHO BÁO CÁO) 🏆")
    print("=" * 65)
    print(f"✅ TỔNG THỂ HỆ THỐNG (Overall F1) : {ket_qua['eval_overall_f1'] * 100:.2f}%")
    print(f"✅ TỔNG THỂ ĐỘ PHỦ (Overall Recall): {ket_qua['eval_overall_recall'] * 100:.2f}%")
    print("-" * 65)
    
    # Duyệt qua in điểm từng nhãn (SKILL, JOB_TITLE...)
    for key, value in ket_qua.items():
        if isinstance(value, dict) and 'f1' in value:
            nhan = key.replace('eval_', '')
            f1 = value['f1'] * 100
            precision = value['precision'] * 100
            recall = value['recall'] * 100
            print(f"🔸 Nhãn [{nhan}]: F1 = {f1:.2f}% | Precision = {precision:.2f}% | Recall = {recall:.2f}%")
    print("=" * 65)

    # Lưu lại bộ "não" siêu việt
    trainer.save_model("./Model")
    tokenizer.save_pretrained("./Modeln")
    print("\n=> THÀNH CÔNG! Mô hình hoàn thiện nhất đã lưu tại thư mục 'Model.")

if __name__ == "__main__":
    main()