python gen_data.py --input_file data/corpus_title_0.txt --split_tr=0.8 --split_va=0.9 --split_te=1.0 --train_file='data/my_title.train' --valid_file='data/my_title.valid' --test_file='data/my_title.test' > log/data_split.log 2>&1
echo "sucessful"