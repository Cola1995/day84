#
# class Page():
#
#     def __init__(self, page_num, total_count, url_prefix, params, per_page=10, max_page=11):
#         """
#
#         :param page_num: 当前页码数
#         :param total_count: 数据总数
#         :param url_prefix: a标签href的前缀
#         :param per_page: 每页显示多少条数据
#         :param max_page: 页面上最多显示几个页码
#         """
#         # print('AAAAAAAAAAAAAAAAAAAAAAAa')
#         # print(per_page,max_page)
#         self.url_prefix = url_prefix
#         self.max_page = max_page
#         # 每一页显示多少条数据
#         # 总共需要多少页码来展示
#         total_page, m = divmod(total_count, per_page)
#         if m:
#             total_page += 1
#         self.total_page = total_page
#
#         try:
#             page_num = int(page_num)
#             # 如果输入的页码数超过了最大的页码数，默认返回最后一页
#             if page_num > total_page:
#                 page_num = total_page
#         except Exception as e:
#             # 当输入的页码不是正经数字的时候 默认返回第一页的数据
#             page_num = 1
#         self.page_num = page_num
#
#         # 定义两个变量保存数据从哪儿取到哪儿
#         # self.data_start = (page_num - 1) * 10
#         # self.data_end = page_num * 10
#         self.data_start = (page_num - 1) * per_page
#         self.data_end = page_num * per_page
#
#
#         # 页面上总共展示多少页码
#         if total_page < self.max_page:
#             self.max_page = total_page
#
#         half_max_page = self.max_page // 2
#         # 页面上展示的页码从哪儿开始
#         page_start = page_num - half_max_page
#         # 页面上展示的页码到哪儿结束
#         page_end = page_num + half_max_page
#         # 如果当前页减一半 比1还小
#         if page_start <= 1:
#             page_start = 1
#             page_end = self.max_page
#         # 如果 当前页 加 一半 比总页码数还大
#         if page_end >= total_page:
#             page_end = total_page
#             page_start = total_page - self.max_page + 1
#         self.page_start = page_start
#         self.page_end = page_end
#
#         import copy
#         self.params = copy.deepcopy(params)  # {"page":"12","title_startwith":"py","id__gt":"5"}
#
#     @property   # 私有方法，不可被外部赋值。相当于private
#     def start(self):
#         return self.data_start
#
#     @property
#     def end(self):
#         return self.data_end
#
#
#     def page_html(self):
#         # 自己拼接分页的HTML代码
#         html_str_list = []
#         # 加上第一页
#         html_str_list.append('<li><a href="{}?page=1">首页</a></li>'.format( self.url_prefix))
#
#         # 判断一下 如果是第一页，就没有上一页
#         if self.page_num <= 1:
#             html_str_list.append('<li class="disabled"><a href="#"><span aria-hidden="true">&laquo;</span></a></li>'.format(self.page_num-1))
#         else:
#             # 加一个上一页的标签
#             html_str_list.append('<li><a href="{}?page={}"><span aria-hidden="true">&laquo;</span></a></li>'.format( self.url_prefix, self.page_num-1))
#
#         for i in range(self.page_start, self.page_end+1):
#             # 如果是当前页就加一个active样式类
#             self.params["page"] = i
#             if i == self.page_num:
#                 tmp = '<li class="active"><a href="{0}?page={1}">{1}</a></li>'.format(self.url_prefix, i)
#             else:
#                 # # {"page":"7","title_startwith":"py","id__gt":"5"}  #  "page=7&title_startwith=py&id__gt=5"
#                 tmp = '<li><a href="{0}?{1}">{2}</a></li>'.format(self.url_prefix, self.params.urlencode(),i)
#
#             html_str_list.append(tmp)
#
#         # 加一个下一页的按钮
#         # 判断，如果是最后一页，就没有下一页
#         if self.page_num >= self.total_page:
#             html_str_list.append('<li class="disabled"><a href="#"><span aria-hidden="true">&raquo;</span></a></li>')
#         else:
#             html_str_list.append('<li><a href="{}?page={}"><span aria-hidden="true">&raquo;</span></a></li>'.format( self.url_prefix, self.page_num+1))
#         # 加最后一页
#         html_str_list.append('<li><a href="{}?page={}">尾页</a></li>'.format( self.url_prefix, self.total_page))
#
#         page_html = "".join(html_str_list)
#         return page_html



class Page(object):
    def __init__(self, current_page, all_count, base_url,params, per_page_num=8, pager_count=11, ):
        """
        封装分页相关数据
        :param current_page: 当前页
        :param all_count:    数据库中的数据总条数
        :param per_page_num: 每页显示的数据条数
        :param base_url: 分页中显示的URL前缀
        :param pager_count:  最多显示的页码个数
        """

        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1

        if current_page < 1:
            current_page = 1

        self.current_page = current_page

        self.all_count = all_count
        self.per_page_num = per_page_num

        self.base_url = base_url

        # 总页码
        all_pager, tmp = divmod(all_count, per_page_num)
        if tmp:
            all_pager += 1
        self.all_pager = all_pager

        self.pager_count = pager_count  # 最多显示页码数
        self.pager_count_half = int((pager_count - 1) / 2)

        import copy
        params = copy.deepcopy(params)
        params._mutable = True
        self.params = params  # self.params : {"page":77,"title":"python","nid":1}


    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_num


    @property
    def end(self):
        return self.current_page * self.per_page_num


    def page_html(self):
        # 如果总页码 < 11个：
        if self.all_pager <= self.pager_count:
            pager_start = 1
            pager_end = self.all_pager + 1
        # 总页码  > 11
        else:
            # 当前页如果<=页面上最多显示(11-1)/2个页码
            if self.current_page <= self.pager_count_half:
                pager_start = 1
                pager_end = self.pager_count + 1

            # 当前页大于5
            else:
                # 页码翻到最后
                if (self.current_page + self.pager_count_half) > self.all_pager:
                    pager_start = self.all_pager - self.pager_count + 1
                    pager_end = self.all_pager + 1

                else:
                    pager_start = self.current_page - self.pager_count_half
                    pager_end = self.current_page + self.pager_count_half + 1

        page_html_list = []
        self.params["page"] = 1
        first_page = '<li><a href="%s?%s">首页</a></li>' % (self.base_url, self.params.urlencode(),)
        page_html_list.append(first_page)

        if self.current_page <= 1:
            prev_page = '<li class="disabled"><a href="#">上一页</a></li>'
        else:
            self.params["page"] = self.current_page - 1
            prev_page = '<li><a href="%s?%s">上一页</a></li>' % (self.base_url, self.params.urlencode(),)

        page_html_list.append(prev_page)

        for i in range(pager_start, pager_end):
            #  self.params  : {"page":77,"title":"python","nid":1}

            self.params["page"] = i  # {"page":72,"title":"python","nid":1}
            if i == self.current_page:
                temp = '<li class="active"><a href="%s?%s">%s</a></li>' % (self.base_url, self.params.urlencode(), i,)
            else:
                temp = '<li><a href="%s?%s">%s</a></li>' % (self.base_url, self.params.urlencode(), i,)
            page_html_list.append(temp)

        if self.current_page >= self.all_pager:
            next_page = '<li class="disabled"><a href="#">下一页</a></li>'
        else:
            self.params["page"] = self.current_page + 1
            next_page = '<li><a href="%s?%s">下一页</a></li>' % (self.base_url, self.params.urlencode(),)
        page_html_list.append(next_page)

        self.params["page"] = self.all_pager
        last_page = '<li><a href="%s?%s">尾页</a></li>' % (self.base_url, self.params.urlencode(),)
        page_html_list.append(last_page)

        return ''.join(page_html_list)