#!/usr/bin/env/py35
# coding=utf-8
import argparse

def splitData(input_file, split_tr, split_va,split_te, train_file, valid_file, test_file):
    with open(input_file, 'r') as fr:
        lines = fr.readlines()
        lines_num = len(lines)
        split_train = int(lines_num*split_tr)
        split_valid = int(lines_num*split_va)
        split_test = int(lines_num * split_te)
        count = 0
        train = open(train_file,'w')
        test = open(test_file,'w')
        valid = open(valid_file,'w')
        for line in lines:
            if line.startswith('_') or line.startswith('36') or line.startswith('氪'):
                continue
            count += 1
            if count < split_train:
                train.write(line)
            elif count >= split_train and count < split_valid:
                valid.write(line)
            elif count >= split_valid and count < split_test:
                test.write(line)

            else:
                pass
        train.close()
        test.close()
        valid.close()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, help='input file to be split', required=True)
    parser.add_argument('--split_tr', type=float, help='define the size of train set', required=True)
    parser.add_argument('--split_va', type=float, help='define the size of valid set', required=True)
    parser.add_argument('--split_te', type=float, help='define the size of test set', default=1.0)
    parser.add_argument('--train_file', type=str, help='train set output', default='train_text.txt')
    parser.add_argument('--valid_file', type=str, help='valid set output', default='valid_text.txt')
    parser.add_argument('--test_file', type=str, help='test set output', default='test_text.txt')
    args = parser.parse_args()
    print("params info:--input_file={}\n\t--split_tr={}\n\t--split_va={}\n\t--split_te={}".format(args.input_file, args.split_tr, args.split_va, args.split_te))
    splitData(args.input_file, args.split_tr, args.split_va, args.split_te, args.train_file, args.valid_file, args.test_file)