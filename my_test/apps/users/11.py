#
# users_list = [{'detail__address': '省北京市', 'counts': 3}, {'detail__address': '杭州', 'counts': 2}, {'detail__address': '长沙', 'counts': 2}, {'detail__address': '重庆', 'counts': 2}, {'detail__address': '新疆', 'counts': 2}, {'detail__address': '洛阳', 'counts': 2}, {'detail__address': '内蒙古', 'counts': 2}, {'detail__address': '温州', 'counts': 1}, {'detail__address': '石家庄', 'counts': 1}, {'detail__address': '南宁', 'counts': 1}, {'detail__address': '乌江', 'counts': 1}, {'detail__address': '海南', 'counts': 1}, {'detail__address': '南京', 'counts': 1}, {'detail__address': '广州', 'counts': 1}, {'detail__address': '湖南', 'counts': 1}, {'detail__address': '上海', 'counts': 1}, {'detail__address': '济南', 'counts': 1}, {'detail__address': '大理', 'counts': 1}, {'detail__address': '成都', 'counts': 1}, {'detail__address': '西安', 'counts': 1}, {'detail__address': None, 'counts': 0}]
# print(users_list)
# lists = [ ]
# for i in users_list:
#     if i["detail__address"]:
#         i["detail__address"]=i["detail__address"].split("省")[-1].split("市")[0]
#         lists.append(i)
#
# users_list=lists
#
# print(users_list)


a = {'dd':1,"cc":2}
b = {'gg':3,"hh":4}
# dictMerged1=dict(a.items()+ b.items())

print(dict(a, **b))