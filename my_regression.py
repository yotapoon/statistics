import statsmodels.api as sm
import numpy as np
import pandas as pd

class my_linear_regression:
    def __init__(self, X, subset = [], file = []): # 欠損値を含む可能性がある列をsubsetで指定してdrop
        self.X = X.copy()
        self.X.dropna(subset = subset, inplace = True)
        self.col_name_list = [] # ダミー変数にした列のリストを保存する
        self.dict_dummy_list = {} # ダミー変数の要素(dropした後のもの)を列の名前ごとに保存
        self.file = file
        self.file_exist = False

    def get_dummies(self, col_name, dummy_full_list, dummy_drop): # 指定した列をダミー変数へ変更
        dummy_list = dummy_full_list[:] # dummy_full_listからremoveするとループがおかしくなる

        # Xに存在しないダミーの要素がdummy_listに入っていたら削除
        for dummy in dummy_full_list:
            if sum(self.X[col_name] == dummy) == 0: # Xがdummyを含まない場合
                dummy_list.remove(dummy)
        dummy_list.remove(dummy_drop) # 多重共線性を回避するために，指定した要素をdrop

        # ダミー変数にする
        for dummy in dummy_list:
            self.X[dummy] = (self.X[col_name].values == dummy) * 1.0

        self.col_name_list.append(col_name) # ダミー変数にした列のリストを保存
        self.dict_dummy_list[col_name] = dummy_list[:] # ダミー変数の要素(dropした後のもの)を列の名前ごとに保存

    def fit(self, target, factor_list, dummy_list = []): # ファクターを指定して回帰する，dummy_listの意味が違っていることに注意
        # 定数項を追加
        factor_list.insert(0, "const")
        self.X["const"] = np.ones(len(self.X))

        # ダミー変数をファクターに追加
        for dummy in dummy_list:
            factor_list = factor_list + self.dict_dummy_list[dummy]
        self.factor_list = factor_list # predictで使用するので保存

        # 回帰
        self.result = sm.OLS(self.X[target], self.X[factor_list]).fit()
        # saveで使用するので保存
        self.df_result = pd.DataFrame(index = self.result.params.index, columns = [])
        self.df_result["coef"] = self.result.params.values
        self.df_result["t"] = self.result.tvalues.values

        display(self.result.summary()) # 一応回帰結果を表示する

    def save(self, sheet_name): # 回帰係数をexcelに保存
        if self.file_exist: # 今回のユニバースでファイルが存在している場合
            with pd.ExcelWriter(self.file, engine = "openpyxl", mode = "a") as writer: # 上書き
                self.df_result.to_excel(writer, sheet_name = sheet_name)
        else: # 今回のユニバースでまだファイルが存在していない場合
            self.df_result.to_excel(self.file, sheet_name) # ファイルの作成
            self.file_exist = True # フラグの更新

    def predict(self): # fitに使用したfactor_listでtargetを推計する
        return self.result.predict(self.X[self.factor_list])
