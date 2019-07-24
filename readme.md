第七届“泰迪杯”数据挖掘挑战赛c题
文件说明：
10tables内为问题一需要提交截图的十张表源数据与预处理后的数据。
		其中以dealed结尾为文件名的文件为预处理后的数据。
score_table内为驾驶行为汇总表、训练集、测试集和最终结果验证数据。
		其中Gatherfile.csv为驾驶行为汇总表；trainset.csv为训练集；testset.csv为测试集；validationset.xlsx为最终结果验证表。
screenshot_video内包括了问题一要求的十辆车的轨迹与相关信息的截图，以及动态轨迹录像。（因为AB00006行驶的县级道路在leaflet地图库中没有收录，所以它的细节部分使用百度坐标系下的动态轨迹页面的截图代替。）
		其中**为动态页面中车辆行驶轨迹的录像。
webpage中存放了车辆行驶轨迹页面
		其中stastic_html文件夹内存放着静态页面，dynamic_html中存放着动态页面。
code内为整个项目中的所有代码与相关文件
		其中china_places.json为包含省市县坐标信息的文件；weather.csv是天气数据；simhei.ttf为黑体字体文件；
		deal_data.py实现数据预处理；run_map.py实现静态页面的生成；Statistic_num.py完成对驾驶行为进行统计；
		separate.py对统计后的数据完成划分成训练集和测试集；bpnn_forscore.py实现BP网络对训练集的训练并应用在测试集上评分。
		extra code文件夹中包含着额外的可视化文件
				其中Heatmap.py实现将汽车的轨迹绘制成热力图；Kmeans.py实现对驾驶行为汇总文件的聚类与可视化。
		dynamic_map文件夹内实现动态轨迹页面的生成