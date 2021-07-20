import statsmodels.api as sm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class my_check_data:
    def __init__(self, X, subset = []): # 欠損値を含む可能性がある列をsubsetで指定してdrop
        self.X = X.copy()
        self.X.dropna(subset = subset, inplace = True)
        self.col_name_list = [] # ダミー変数にした列のリストを保存する
        self.dict_dummy_list = {} # ダミー変数の要素を列の名前ごとに保存

    def get_dummies(self, col_name, dummy_full_list): # 指定した列をダミー変数へ変更
        dummy_list = dummy_full_list[:] # dummy_full_listからremoveするとループがおかしくなる

        # ダミー変数にする
        for dummy in dummy_list:
            self.X[dummy] = (self.X[col_name].values == dummy) * 1

        self.col_name_list.append(col_name) # ダミー変数にした列のリストを保存
        self.dict_dummy_list[col_name] = dummy_list[:] # ダミー変数の要素を列の名前ごとに保存

    # 単体の変数の分布
    def quantitative_factor(self, factor_list, file): # 量的変数の分布をヒストグラムで確認する
        # ヒストグラムの表示
        plt.figure(figsize = (4*len(factor_list), 4))
        for idx, factor in enumerate(factor_list):
            plt.subplot(1, len(factor_list), idx + 1)
            plt.hist(self.X[factor], bins = 20, label = factor)
            plt.xlabel(factor, fontsize = 18)
            plt.ylabel("frequency", fontsize = 18)
        plt.tight_layout()
        # ファイルの出力
        with pd.ExcelWriter(file) as writer:
            for factor in factor_list:
                self.X[factor].to_excel(writer, sheet_name = factor, index = False)

    def qualitative_factor(self, col_name, file, vertical = False): # 質的変数の分布を棒グラフで確認する
        # テーブルの作成
        dummy_list = self.dict_dummy_list[col_name] # ダミー変数のリスト
        df = pd.DataFrame(index = dummy_list, columns = ["number"], dtype = "int")
        df["number"] = self.X[dummy_list].sum().T # ダミー列をデータ方向に足し合わせる

        if vertical: # 横棒グラフを出力したい場合は，順序を変更する必要がある．
            df = df[::-1].copy()
        # ファイルの出力
        with pd.ExcelWriter(file) as writer:
            df.to_excel(writer, sheet_name = col_name)

        # 棒グラフの出力
        plt.figure(figsize = (4, 0.5*len(df)))
        position = np.arange(len(df))
        plt.barh(position, df["number"])
        plt.xlabel("frequency", fontsize = 12)
        plt.yticks(position, df.index)

    # 二つの変数の相関
    def quantitative_vs_qualitative(self, factor_list, col_name, file):
        # テーブルの作成
        dummy_list = self.dict_dummy_list[col_name] # ダミー変数のリスト
        df = self.X[[col_name] + factor_list].copy()
        df["temp"] = 0.0 # ソートに使用する列を作成
        for idx, dummy in enumerate(dummy_list):
            df.loc[df[col_name] == dummy, "temp"] = idx # ダミーの順序に応じて値をつける
        df.sort_values(by = "temp", inplace = True) # 新しく作った列を利用してソート

        # ファイルの出力
        with pd.ExcelWriter(file) as writer:
            for factor in factor_list:
                df[[col_name] + [factor]].to_excel(writer, sheet_name = factor, index = False)
