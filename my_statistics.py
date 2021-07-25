import statsmodels.api as sm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openpyxl

# ヒートマップのオプションを増やすこともできる

class my_check_data:
    def __init__(self, X, subset = [], file_name = []): # 欠損値を含む可能性がある列をsubsetで指定してdrop
        self.X = X.copy()
        self.X.dropna(subset = subset, inplace = True)
        self.col_name_list = [] # ダミー変数にした列のリストを保存する
        self.dict_dummy_list = {} # ダミー変数の要素を列の名前ごとに保存
        self.file_name = file_name
        self.file_exist = False

    def get_dummies(self, col_name, dummy_full_list = []): # 指定した列をダミー変数へ変更
        if len(dummy_full_list) == 0:
            dummy_list = list(self.X[col_name].unique())
        else:
            dummy_list = dummy_full_list[:] # dummy_full_listからremoveするとループがおかしくなる

        # ダミー変数にする
        for dummy in dummy_list:
            self.X[dummy] = (self.X[col_name].values == dummy) * 1

        self.col_name_list.append(col_name) # ダミー変数にした列のリストを保存
        self.dict_dummy_list[col_name] = dummy_list[:] # ダミー変数の要素を列の名前ごとに保存

    def save(self, df_save, sheet_name, index = False): # excelに保存する
        if self.file_exist: # 今回のユニバースでファイルが存在している場合
            work_book = openpyxl.load_workbook(self.file_name + ".xlsx") # 同じ名前のシートが存在しているときには削除して上書き
            exist_sheet_name = False
            for work_sheet in work_book.worksheets:
                if work_sheet.title == sheet_name:
                    exist_sheet_name = True
            if exist_sheet_name: # 同じ名前のシートが存在しているとき
                del work_book[sheet_name] # 当該シートを削除
                work_book.save(self.file_name + ".xlsx") # 保存しないと変更が反映されない
            with pd.ExcelWriter(self.file_name + ".xlsx", engine = "openpyxl", mode = "a") as writer: # 上書き
                df_save.to_excel(writer, sheet_name = sheet_name, index = index)
        else: # 今回のユニバースでまだファイルが存在していない場合
            df_save.to_excel(self.file_name + ".xlsx", sheet_name = sheet_name, index = index) # ファイルの作成
            self.file_exist = True # フラグの更新

    def get_existing_dummy(self, col_name): # ダミー変数のうち，存在しているものだけを返す
        # テーブルの作成
        dummy_list = self.dict_dummy_list[col_name][:] # ダミー変数のリスト
        for dummy in self.dict_dummy_list[col_name]:
            if self.X[dummy].sum() == 0: # dummyという値を持つ行が存在しない場合
                dummy_list.remove(dummy) # リストから削除する
        return dummy_list

    # 単体の変数の分布
    ## 量的変数の分布をヒストグラムで確認する
    def quantitative_factor(self, factor_list):
        # ヒストグラムの表示
        plt.figure(figsize = (4*len(factor_list), 4))
        for idx, factor in enumerate(factor_list):
            plt.subplot(1, len(factor_list), idx + 1)
            plt.hist(self.X[factor], bins = 20, label = factor)
            plt.xlabel(factor, fontsize = 18)
            plt.ylabel("frequency", fontsize = 18)
        plt.tight_layout()

        # ファイルへの出力
        for factor in factor_list:
            self.save(self.X[factor], sheet_name = factor, index = False)

    ## 質的変数の分布を棒グラフで確認する
    def qualitative_factor(self, col_name, vertical = False, show_existing_only = True, order_by_number = False): # デフォルトは縦棒グラフ，vertical = Trueとすると横棒グラフ
        # テーブルの作成
        if show_existing_only:
            dummy_list = self.get_existing_dummy(col_name)
        else:
            dummy_list = self.dict_dummy_list[col_name][:]
        df = pd.DataFrame(index = dummy_list, columns = ["number"], dtype = "int")
        df["number"] = self.X[dummy_list].sum().T # ダミー列をデータ方向に足し合わせる

        if order_by_number:
            df.sort_values(by = "number", inplace = True, ascending = False)

        if vertical: # 横棒グラフを出力したい場合
            df = df[::-1].copy() # 順序を適当に変換
        # ファイルの出力
        self.save(df, sheet_name = col_name, index = True)

        # グラフの出力
        position = np.arange(len(df))

        if not vertical: # 縦棒グラフの場合
            plt.bar(position, df["number"])
            plt.ylabel("frequency", fontsize = 12)
            plt.xticks(position, df.index)
        else:
            # 棒グラフの出力
            #plt.figure(figsize = (4, 0.5*len(df)))
            plt.barh(position, df["number"])
            plt.xlabel("frequency", fontsize = 12)
            plt.yticks(position, df.index)

    # 二つの変数の相関

    ## 量的変数 vs 量的変数の分布を散布図で確認する
    def quantitative_vs_quantitative(self, factor1_list, factor2_list, alpha = 0.4, fontsize_label = 14, fontsize_title = 14): # factor1が行となり，factor2が列となるイメージ
        # 散布図の作成
        plt.figure(figsize = (4*len(factor2_list), 4*len(factor1_list)))
        for idx1, factor1 in enumerate(factor1_list):
            for idx2, factor2 in enumerate(factor2_list):
                plt.subplot(len(factor1_list), len(factor2_list), idx1*len(factor2_list) + idx2 + 1)
                plt.scatter(self.X[factor2], self.X[factor1], alpha = alpha)
                plt.xlabel(factor2, fontsize = fontsize_label, fontname = "MS Gothic")
                plt.ylabel(factor1, fontsize = fontsize_label, fontname = "MS Gothic")
                plt.title(factor2 + " vs " + factor1, fontsize = fontsize_title, fontname = "MS Gothic")
        plt.tight_layout()

        # ファイルの出力
        for factor1 in factor1_list:
            for factor2 in factor2_list:
                self.save(self.X[[factor1, factor2]], sheet_name = factor1 + " vs " + factor2, index = False)

    ## 質的変数 vs 質的変数の分布をヒートマップで確認する
    def qualitative_vs_qualitative(self, col_name1, col_name2, show_existing_only1 = True, show_existing_only2 = True):
        # テーブルの作成
        if show_existing_only1:
            dummy1_list = self.get_existing_dummy(col_name1)
        else:
            dummy1_list = self.dict_dummy_list[col_name1][:]

        if show_existing_only2:
            dummy2_list = self.get_existing_dummy(col_name2)
        else:
            dummy2_list = self.dict_dummy_list[col_name2][:]

        df = self.X[dummy1_list].T.dot(self.X[dummy2_list]) # ダミー変数としているから積によって計算できる
        # ファイルの出力
        self.save(df, sheet_name = col_name1 + " vs " + col_name2, index = True) # ここはindexをTrueにしないとヒートマップにならない
        # ヒートマップの出力
        ## 数値あり，整数
        sns.heatmap(df.astype(int), annot = True, fmt = "g", cmap = "Blues")


    ## 質的変数 vs 量的変数の分布を箱ひげ図で確認する
    def qualitative_vs_quantitative(self, col_name, factor_list, vertical = False, show_existing_only = True): # デフォルトではダミーが縦に並ぶイメージ
        # テーブルの作成
        if show_existing_only:
            dummy_list = self.get_existing_dummy(col_name)
        else:
            dummy_list = self.dict_dummy_list[col_name][:]

        df = self.X[[col_name] + factor_list].copy()
        df["temp"] = 0.0 # ソートに使用する列を作成
        for idx, dummy in enumerate(dummy_list):
            df.loc[df[col_name] == dummy, "temp"] = idx # ダミーの順序に応じて値をつける
        df.sort_values(by = "temp", inplace = True) # 新しく作った列を利用してソート

        # ファイルの出力
        for factor in factor_list:
            self.save(df[[col_name] + [factor]], sheet_name = col_name + " vs " + factor, index = False)

        # 箱ひげ図の作成
        if vertical: # ダミー変数が列として横に並ぶ
            plt.figure(figsize = (len(dummy_list), 4*len(factor_list)))
            for idx_factor, factor in enumerate(factor_list):
                plt.subplot(len(factor_list), 1, idx_factor + 1)
                x_dummy = [[] for _ in range(len(dummy_list))] # ダミーの値に対応するファクターのリストを格納する
                for idx_dummy, dummy in enumerate(dummy_list):
                    x_dummy[idx_dummy] = self.X[self.X[col_name] == dummy][factor] # dummyに対応するfactorの値をリストとして保存
                plt.boxplot(x_dummy, vert = True, labels = dummy_list)
                plt.xlabel(factor, fontsize = 14, fontname = "MS Gothic")
        else: # ダミー変数が行として縦に並ぶ
            dummy_list = dummy_list[::-1] # ダミーの順序を変更しないといい感じに表示されない
            plt.figure(figsize = (4*len(factor_list), len(dummy_list)))
            for idx_factor, factor in enumerate(factor_list):
                plt.subplot(1, len(factor_list), idx_factor + 1)
                x_dummy = [[] for _ in range(len(dummy_list))] # ダミーの値に対応するファクターのリストを格納する
                for idx_dummy, dummy in enumerate(dummy_list):
                    x_dummy[idx_dummy] = self.X[self.X[col_name] == dummy][factor] # dummyに対応するfactorの値をリストとして保存
                plt.boxplot(x_dummy, vert = False, labels = dummy_list)
                plt.xlabel(factor, fontsize = 14, fontname = "MS Gothic")
