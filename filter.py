import pandas as pd
import argparse

# 读取词库
dirty_words_df = pd.read_csv('脏话词库.csv', usecols=[0], header=None, names=['word'])
porn_words_df = pd.read_csv('色情词库.csv', usecols=[0], header=None, names=['word'])
dirty_words_df['type'] = '脏话'
porn_words_df['type'] = '色情词汇'
sensitive_words_df = pd.concat([dirty_words_df, porn_words_df], ignore_index=True)

# 检查是否存在同时属于脏话和色情词汇的词
word_type_dict = {}
for _, row in sensitive_words_df.iterrows():
    word, word_type = row['word'], row['type']
    if word in word_type_dict:
        word_type_dict[word].add(word_type)
    else:
        word_type_dict[word] = {word_type}

# 检查敏感词时，优先选择更长的字符串进行比对
def check_sensitive_words(text, word_type_dict):
    detected_words = set()
    checked_words = set()  # 已检查过的词汇
    words_sorted_by_length = sorted(word_type_dict.keys(), key=len, reverse=True)
    
    for word in words_sorted_by_length:
        types = word_type_dict[word]
        if word in checked_words:  # 如果已经检查过该词，则跳过
            continue
        
        if word in text:
            # 将 types 转换为元组或列表以确保可哈希性
            detected_words.add((word, tuple(types)))
            # 标记所有较短的词汇已经被检查过
            for i in range(len(word)):
                for j in range(i + 1, len(word) + 1):
                    checked_words.add(word[i:j])
    
    return detected_words

def calculate_proportion(text, detected_words):
    # 计算文本中的总字符数
    total_characters = len(text)  
    sensitive_characters_count = 0
    
    # 统计敏感词的字符出现次数
    for word, _ in detected_words:
        sensitive_characters_count += text.count(word) * len(word)
    
    if total_characters > 0:
        proportion = sensitive_characters_count / total_characters
    else:
        proportion = 0.0
    
    return proportion

def main():
    parser = argparse.ArgumentParser(description='检查文本中的敏感词并计算比例。')
    parser.add_argument('text', type=str, help='要检查的文本')
    args = parser.parse_args()

    text_to_check = args.text

    # 检查文本中的敏感词
    detected_words = check_sensitive_words(text_to_check, word_type_dict)

    # 输出原文和检测到的敏感词
    print(f"原文: {text_to_check}")

    if detected_words:
        for word, types in detected_words:
            if '脏话' in types and '色情词汇' in types:
                print(f"检测到脏话和色情词汇: {word}")
            elif '脏话' in types:
                print(f"检测到脏话: {word}")
            elif '色情词汇' in types:
                print(f"检测到色情词汇: {word}")
        
        proportion = calculate_proportion(text_to_check, detected_words)
        print(f"含有脏话和色情词汇的比例: {proportion:.2%}")
    else:
        print("未检测到敏感词。")

if __name__ == '__main__':
    main()
