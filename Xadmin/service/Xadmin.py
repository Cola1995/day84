from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from Xadmin.utils.page import Page
from django.db.models import Q

from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related import ManyToManyField
class ShowList(object):
    """
    显示数据类
    """
    def __init__(self,config,data_list,request):
        self.config=config
        self.data_list=data_list
        self.request = request

        data_count = self.data_list.count()
        current_page = int(self.request.GET.get("page", 1))
        base_path = self.request.path
        # 调用分页器方法
        self.pagination = Page(current_page, data_count, base_path, self.request.GET, per_page_num=5,
                               pager_count=11, )
        self.page_data = self.data_list[self.pagination.start:self.pagination.end]

        # actions
        self.actions = self.config.get_new_actions()  # [patch_init,]

    def get_action_list(self):
        temp = []
        for action in self.actions:
            temp.append({
                "name": action.__name__,
                "desc": action.short_description
            })  # [{"name":""patch_init,"desc":"批量初始化"}]

        return temp


    def get_header(self):
        header_list = []

        for field in self.config.list_display1():  # [check,"nid","title","publish",edit,delete]
            # print("调试",field)    # self.config.list_display1（）是空情况则 ['__str__']
            if isinstance(field, str):  #
                if field == "__str__":
                    val = self.config.model._meta.model_name.upper()
                else:
                    field_obj = self.config.model._meta.get_field(field)
                    val = field_obj.verbose_name

            else:
                val = field(self.config, is_header=True)  # 获取表头，传is_header=True
            header_list.append(val)
        return header_list

    def get_data_list(self):
        new_data_list = []

        for i in self.page_data:
            temp = []
            for fied in self.config.list_display1():
                if isinstance(fied, str):
                    # 处理多多对多数据显示问题
                    try:   #  如果没有配置list_display，循环  默认返回model 对象__str__ 值
                        from django.db.models.fields.related import ManyToManyField
                        field_obj = self.config.model._meta.get_field(fied)
                        t = []
                        if isinstance(field_obj,ManyToManyField): # 如果是多对多对象，取值是[obj1,obj2]
                            val = getattr(i, fied).all()
                            for data_obj in val:
                                t.append(str(data_obj))
                            val = ",".join(t)
                        else:  # 普通对象直接取值，如果是__str__,则捕获异常
                            val = getattr(i, fied)       # 反射取对象中的值
                            if fied in self.config.list_display_links:    # 循环数据，如果配置list_disaplay 则返回反向解析url跳转连接
                                r_url = reverse('%s_%s_change' % (self.config.model._meta.app_label, self.config.model._meta.model_name),
                                                args=(i.pk,))
                                val = mark_safe("<a href='%s'>%s</a>"%(r_url, val))
                    except Exception as e:
                        val = getattr(i, fied)

                else:
                    val = fied(self.config, i)   # 传入当前query set 对象,执行编辑，删除，复选框函数
                temp.append(val)
            new_data_list.append(temp)
            # print("______________")
            # print(new_data_list)
        # new_data_list = [
        #     ['红与黑',12],
        #     ['python',11],
        #
        # ]
        return new_data_list

    def get_filter_tag(self):
        link_tag = {}
        print("aaaaaaaaaaaaaa",type(self.request.GET))
        import copy
        for field in self.config.list_filter:  # 循环过滤对象列表
            params = copy.deepcopy(self.request.GET)
            # print(type(params))
            # params = self.request.GET
            model_field = self.config.model._meta.get_field(field)    #获取对应model字段


            if isinstance(model_field,ForeignKey) or isinstance(model_field,ManyToManyField):
                print("okokokoo")
                data_list = model_field.rel.to.objects.all()
            else:
                data_list = self.config.model.objects.all().values('pk', field)
            print(data_list)

            cid = self.request.GET.get(field, 0)
            temp = []
            # 处理全部
            if self.request.GET.get(field):
                del params[field]
                temp.append("<a href='?%s'>全部</a>"%params.urlencode())
            else:
                temp.append("<a href='#' class='active'>全部</a>")


            # 处理数据标签
            for obj in data_list:

                if isinstance(model_field, ForeignKey) or isinstance(model_field, ManyToManyField):
                    pk = obj.pk
                    text = str(obj)
                    params[field] = pk
                    print("111111111111111111111111111")
                    print(obj)
                    print(text)
                else:  # data_list= [{"pk":1,"title":"go"},....]
                    print("========")
                    pk = obj.get("pk")
                    text = obj.get(field)
                    params[field] = text
                    print("@@@@@@@@@@@@@@@@@")
                    print(text)
                # params[field] = obj.pk
                _url = params.urlencode()  # ['pk':1]  --->&pk=1
                if cid==str(pk) or cid==text:
                    a = "<a href='?%s' class='active'>%s</a>"%(_url, text)
                else:
                    a = "<a href='?%s'>%s</a>"%(_url, text)

                temp.append(a)
                link_tag["By "+field] = temp
        return link_tag



class ModelXadmin(object):
    list_display = ["__str__"]
    list_display_links = []
    modelform_class = None
    search_fields = []
    actions = []
    list_filter = []

    def patch_dele(self, request, queryset):
        # print(queryset)
        queryset.delete()
    patch_dele.short_description = "批量删除"


    def __init__(self, model, site):
        self.model = model
        self.site = site
    # check 编辑 删除

    def edit(self, obj=None, is_header=False):
        if is_header:
            return "操作"

        r_url = reverse('%s_%s_change'%(self.model._meta.app_label, self.model._meta.model_name), args=(obj.pk,))

        # return mark_safe("<a href='%s/change/'>编辑</a>"%obj.pk)
        return mark_safe("<a href='%s'>编辑</a>"%r_url)

    def dele(self,obj = None, is_header=False):
        if is_header:
            return "操作"
        r_url = reverse('%s_%s_dele' % (self.model._meta.app_label, self.model._meta.model_name), args=(obj.pk,))
        return mark_safe("<a href='%s'>删除</a>"%r_url)

    def che(self, obj=None, is_header=False):
        if is_header:
            return "操作"
        return mark_safe("<input type='checkbox' name='select_pk' value='%s' >"%obj.pk)

    def list_display1(self):
        """
        重构list-display
        :return:
        """
        t = []
        t.append(ModelXadmin.che)
        t.extend(self.list_display)
        if not self.list_display_links:
            t.append(ModelXadmin.edit)
        t.append(ModelXadmin.dele)
        return t

    def get_new_actions(self):

        temp = []
        temp.append(ModelXadmin.patch_dele)
        temp.extend(self.actions)
        return temp

    def get_add_url(self):

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("%s_%s_add" % (app_label, model_name))

        return _url

    def get_list_url(self):
        """
        反向解析方法
        :return:
        """
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label
        _url = reverse("%s_%s_list" % (app_label, model_name))

        return _url

    def get_modelform_class(self):
        """
        获取自定制modelform 方法
        :return:
        """
        if not self.modelform_class:
            from django.forms import ModelForm
            class ModelFormDemo(ModelForm):
                class Meta:
                    model = self.model
                    fields = "__all__"
                    labels = {
                        ""
                    }

            return ModelFormDemo
        else:
            return self.modelform_class

    def get_search(self, request):
        search_info = request.GET.get("search", "")
        self.search_info = search_info
        search_Q = Q()
        search_Q.connector = "or"
        for field in self.search_fields:
            search_Q.children.append((field + "__contains", search_info))
        return search_Q

    def get_filter_search(self, request):
        filter_Q = Q()
        for k,v in request.GET.items():
            if k in self.list_filter:
                filter_Q.children.append((k,v))

        return filter_Q



    def list_view(self, request):

        # search_info = request.GET.get("search", "")
        #
        # search_Q = Q()
        # search_Q.connector = "or"
        # for field in self.search_fields:
        #     search_Q.children.append((field+"__contains",search_info))
        print("listview")
        print(request.POST)
        if request.method == "POST":  # action
            print("POST:", request.POST)
            action = request.POST.get("action")
            selected_pk = request.POST.getlist("select_pk")
            action_func = getattr(self, action)
            queryset = self.model.objects.filter(pk__in=selected_pk)
            ret = action_func(request, queryset)

        search_Q = self.get_search(request)   # 查找配置的search列表 title or price

        filter_Q = self.get_filter_search(request)


        data_list = self.model.objects.all().filter(search_Q).filter(filter_Q)
        print("####",data_list)
        model_name = self.model._meta.model_name
        showlist = ShowList(self,data_list,request)
        add_url = self.get_add_url()
        return render(request, 'list_view.html', locals())

    def add_view(self, request):
        model_name = self.model._meta.model_name
        ModelFormDemo = self.get_modelform_class()
        form = ModelFormDemo()
        # 处理加号问题 关键点是 判断form对象是否是 <class 'django.forms.models.ModelChoiceField'>
        from django.forms.models import ModelChoiceField
        for model_field in form:
            print(model_field.field)
            print(type(model_field.field))
            if isinstance(model_field.field, ModelChoiceField):
                model_field.is_pop = True            # 如果是添加标识，前端根据标识判断是否显示加号
                releted_app_name = model_field.field.queryset.model._meta.app_label  # 关联表app name
                releted_model_name = model_field.field.queryset.model._meta.model_name  # 关联表 model name
                # pop_res = model_field.field.queryset.model._meta.
                print("一对多表",model_field.field.queryset.model,releted_app_name,releted_model_name)
                _url = reverse("%s_%s_add"%(releted_app_name,releted_model_name))
                model_field.url = _url+"?pop_res=id_%s"%model_field.name   # 传字段值
        # 如果有数据提交的情况
        if request.method == "POST":
            form = ModelFormDemo(request.POST)
            if form.is_valid():  # 校验通过 数据保存
                obj = form.save()
                pop_res_id = request.GET.get('pop_res')
                if pop_res_id:   # 关联页面添加
                    res = {"pk": obj.pk, "text": str(obj), "pop_res_id": pop_res_id}
                    return render(request, "pop.html", {"res": res})
                else:   # 正常页面添加

                    return redirect(self.get_list_url())  # 返回当前数据展示页面
            # return render(request, "add_view.html", locals())   # 否则带着错误信息的form回到添加页面

        return render(request, "add_view.html", locals())


    def change_view(self, request, id):
        model_name = self.model._meta.model_name
        ModelFormDemo = self.get_modelform_class()
        edit_obj = self.model.objects.filter(pk=id).first()

        if request.method == "POST":
            form = ModelFormDemo(request.POST, instance=edit_obj)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())

            return render(request, "add_view.html", locals())

        form = ModelFormDemo(instance=edit_obj)

        return render(request, "change_view.html", locals())

    def delete_view(self, request, id):
        url = self.get_list_url()
        if request.method == "POST":
            self.model.objects.filter(pk=id).delete()
            return redirect(url)

        return render(request, "delete_view.html", locals())


    def get_urls2(self):
        temp = []
        temp.append(url(r"^$", self.list_view, name="%s_%s_list"%(self.model._meta.app_label, self.model._meta.model_name)))
        temp.append(url(r"^add/$", self.add_view, name="%s_%s_add"%(self.model._meta.app_label, self.model._meta.model_name)))
        temp.append(url(r"^(\d+)/change/$", self.change_view, name="%s_%s_change"%(self.model._meta.app_label, self.model._meta.model_name)))
        temp.append(url(r"^(\d+)/delete/$", self.delete_view, name="%s_%s_dele"%(self.model._meta.app_label, self.model._meta.model_name)))

        return temp

    @property
    def urls2(self):
        return self.get_urls2(), None, None


class XadminSite(object):
    def __init__(self, name='admin'):
        self._registry = {}

    def get_urls(self):

        print(self._registry)  # {Book:modelAdmin(Book),.......}

        temp = []
        for model, admin_class_obj in self._registry.items():
            app_name = model._meta.app_label
            model_name = model._meta.model_name

            temp.append(url(r'^{0}/{1}/'.format(app_name, model_name), admin_class_obj.urls2))

            '''
            url(r"app01/book",ModelXadmin(Book,site).urls2)
            url(r"app01/publish",ModelXadmin(Publish,site).urls2)
            url(r"app02/order",ModelXadmin(Order,site).urls2)

            '''
        return temp

    @property
    def urls(self):

        return self.get_urls(), None, None

    def register(self, model, admin_class=None, **options):
        if not admin_class:
            admin_class = ModelXadmin

        self._registry[model] = admin_class(model, self)  # {Book:ModelAdmin(Book),Publish:ModelAdmin(Publish)}
site = XadminSite()
