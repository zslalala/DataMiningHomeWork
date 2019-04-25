# coding = utf-8
from RelatedFunction import *
import gc

DataTable = pandas.read_csv("cbg_patterns.csv");

# 剔除全空值的列
DataTable = DataTable.dropna(axis=1, how='all');
# 标称属性
NominalAttribute = ['visitor_home_cbgs', 'visitor_work_cbgs', 'related_same_day_brand',
                    'related_same_month_brand','top_brands','popularity_by_hour','popularity_by_day'
                    ];
# 标称属性摘要，是字典的字典，外层字典的键是属性列名，内层字典的键是各属性的取值
NominalAttributeAbstract = dict();

# 二值属性：本数据集二值属性为空
BinaryAttribute = [];

# 数值属性
NumericAttribute = ['date_range_start', 'date_range_end','raw_visit_count','raw_visitor_count','distance_from_home'];
# 数值属性摘要，是字典，键是属性列名，依次表示最大、最小、均值、中位数、四分之一位数、四分之三位数、缺失值个数
NumericAttributeAbstract = dict();

# 冗余属性
# Completed Date会与Current Status Date相同、Record ID是无用属性、TIDF Compliance只有两个有效元组
RedundantAttribute = ['census_block_group','visitor_home_cbgs', 'visitor_work_cbgs','date_range_start', 'date_range_end'];

# 丢弃冗余属性
DataTable = DataTable.drop(columns=RedundantAttribute);

DataTable[['raw_visitor_count']] = DataTable[['raw_visitor_count']].fillna(value=0);

DataTable[['distance_from_home']] = DataTable[['distance_from_home']].fillna(value=0);
# Apriori算法只能处理二值属性列，需要把标称属性列、数值属性列给离散化，转换为二值属性
# 把部分感兴趣的属性列作离散化

DataTable2 = DataTable[0:3000]
if os.path.exists('new.CSV') == False:
    DataTable = ParticalDiscretization(DataTable2, ['related_same_day_brand','related_same_month_brand','top_brands','popularity_by_hour','popularity_by_day'],
                                       ['raw_visit_count','raw_visitor_count','distance_from_home'], BinaryAttribute);
    DataTable.to_csv(path_or_buf='new.CSV');
else:
    DataTable2 = pandas.read_csv("new.CSV");

# 获取当前可用的列
CurrentAvailableAttribute = list(DataTable.columns);

# 项集的最小支持度
MinimalSupport = 100;

# 所有频繁项集的集合，第一个元素是频繁一项集，第二个元素是频繁二项集，第三个元素是频繁三项集，依次类推
frequentItemsetSet = [];

# 非频繁项集，杂糅包含各个非频繁的项
infrequentItemset = [];

gc.collect()

for i in range(len(CurrentAvailableAttribute)):
    # 最长的项包含所有属性列
    if frequentItemsetSet:
        # FrequentItemsetSet非空，生成频繁k项集
        lastItemset = frequentItemsetSet[-1];
        currentItemset, infrequentItemset = GenerateKItemset(DataTable, MinimalSupport, CurrentAvailableAttribute,
                                                             lastItemset, infrequentItemset);
        if currentItemset:
            frequentItemsetSet.append(currentItemset)
        else:
            print('没有更长的频繁项模式了，频繁模式挖掘完毕');
            break;
    else:
        # FrequentItemsetSet为空，生成频繁一项集
        currentItemset, infrequentItemset = GenerateSingleItemset(DataTable, MinimalSupport, CurrentAvailableAttribute);
        frequentItemsetSet.append(currentItemset)
        pass;

# 项集的最小置信度
MinimalConfidence = 0.8;

for i in frequentItemsetSet:
    print('频繁', len(i[0].m_item), '项:');
    for j in i:
        SubItem = GenerateSubItem(j.m_item);
        for antecedent in SubItem:
            consequent = list(set(j.m_item) ^ set(antecedent));
            consequent_support = ((DataTable[consequent] == 1).sum(axis=1) == len(
                consequent)).sum();
            antecedent_support = ((DataTable[antecedent] == 1).sum(axis=1) == len(
                antecedent)).sum();
            confidence = j.m_support / consequent_support;
            if confidence > MinimalConfidence:
                lift = j.m_support / consequent_support;
                print(antecedent, '=>', consequent, '置信度:', confidence, '提升度:', lift);
