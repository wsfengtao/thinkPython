Vue.config.delimiters = ['${', '}']

// 导航栏数据模型
var navHtmlModel = new Vue({
    el: '#nav4html',
    data: {},
    methods: {
        logout: function() {
            this.$http.post('/admin/logout').then(function(response) {
                if (response.data.code == 200) {
                    alert("注销成功!");
                    //重定向到当前页进行刷新
                    window.location.href = "/admin";
                } else {
                    alert('注销失败!');
                    //重定向到当前页进行刷新
                    window.location.href = "/admin";
                }
            }, function() {
                alert('服务器异常!');
            });
        }
    }
})

// 学员信息模块模型
var student_module = new Vue({
    el: '#student_module',
    data: {
        students4page: [],
        nowpage: 1,
        allpage: 1,
        deletestus: [],
        apply_id: '',
        username: '',
        identy_card_number: '',
        sexpicked: 'option1',
        id_ok: 0,
        id_error: 0,
        name_ok: 0,
        name_error: 0,
        number_ok: 0,
        number_error: 0
    },
    // 初始化加载数据
    ready: function() {
        //启动遮罩
        $("#zhezhao").css("display", "block");
        this.$http.get('/admin/students?nowpage=' + this.nowpage).then(function(response) {
            this.resetstudents4page(response.data);
            //关闭遮罩
            $("#zhezhao").css("display", "none");
        }, function() {
            //关闭遮罩
            $("#zhezhao").css("display", "none");
            alert('服务器异常!');
        });
        $('#myModal').on('hidden.bs.modal', this.clean_mymodel);
    },
    methods: {
        //转换时间戳
        getLocalTime: function(nS) {
            datet = new Date(parseInt(nS) * 1000).toLocaleString().replace(/年|月/g, "-").replace(/日/g, " ");
            first = datet.substr(0, 10);
            end = datet.substr(16, 20);
            return first + end;
        },

        //左扩展
        clk_left_extend: function() {
            if (this.nowpage != 1) {
                this.refreshstu(1);
            }
        },

        //右扩展
        clk_right_extend: function() {
            if (this.nowpage != this.allpage) {
                this.refreshstu(this.allpage);
            }
        },

        // 分页点击
        clkfenye: function(page) {
            if (!(page == this.nowpage)) {
                this.refreshstu(page);
            }
        },
        // 清空输入框校验标志
        clean_input_error: function(key) {
            if (key === 'id') {
                this.id_ok = 0;
                this.id_error = 0;
            } else if (key === 'name') {
                this.name_ok = 0;
                this.name_error = 0;
            } else if (key === 'number') {
                this.number_ok = 0;
                this.number_error = 0;
            }
        },
        // 重置students4page数据(切记信息完整)
        resetstudents4page: function(data) {
            for (var key in data) {
                if (key == 'nowpage' || key == 'allpage') {
                    if (key == 'nowpage') {
                        this.nowpage = parseInt(data[key]);
                    } else {
                        this.allpage = parseInt(data[key]);
                    }
                } else {
                    parseInt(data[key].sex) == 1 ? data[key].sex = '男' : data[key].sex = '女';
                    data[key].create_time = this.getLocalTime(data[key].create_time);
                    this.students4page.push(data[key]);
                }
            }
        },

        //全选
        selectall: function() {
            if ($("#check_all").prop("checked")) {
                $(".check_cld").each(
                    function() {
                        $(this).prop("checked", true);
                    }
                );
            } else {
                $(".check_cld").each(
                    function() {
                        $(this).prop("checked", false);
                    }
                );
            }
        },
        //新建学员信息提交
        addstu: function() {
            //启动遮罩
            $("#zhezhao").css("display", "block");
            postdata = {
                'apply_id': this.apply_id,
                'username': this.username,
                'identy_card_number': this.identy_card_number,
                'sexpicked': this.sexpicked
            };
            if (this.apply_id.match(/\d{12,14}/) && this.username.match(/[\u4E00-\u9FA5]{2,4}/) && this.identy_card_number.match(/(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/)) {
                this.$http.post('/admin/students', postdata).then(function(response) {
                    //关闭遮罩
                    $("#zhezhao").css("display", "none");
                    if (response.data.code == 200) {
                        alert('新增成功!学员信息已经更新!');
                    } else if (response.data.code == 404) {
                        alert('已经存在该用户!');
                    } else if (response.data.code == 411) {
                        alert('数据库异常!');
                    } else {
                        alert('服务器异常!');
                    }
                    // 隐藏模态对话框
                    $('#myModal').modal('hide');
                    //刷新学员信息
                    this.refreshstu();
                }, function() {
                    //关闭遮罩
                    $("#zhezhao").css("display", "none");
                    alert('服务器异常!');
                });
            } else {
                if (!this.apply_id.match(/\d{1,14}/)) {
                    this.id_error = 1;
                } else {
                    this.id_ok = 1;
                }
                if (!this.username.match(/[\u4E00-\u9FA5]{2,4}/)) {
                    this.name_error = 1;
                } else {
                    this.name_ok = 1;
                }
                if (!this.identy_card_number.match(/(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/)) {
                    this.number_error = 1;
                } else {
                    this.number_ok = 1;
                }
                //关闭遮罩
                $("#zhezhao").css("display", "none");
            }
        },
        //刷新当前页学员信息
        refreshstu: function(page) {
            if (!(typeof(page) == 'number')) {
                page = this.nowpage;
            }
            is_alert = (page == this.nowpage);
            //启动遮罩
            $("#zhezhao").css("display", "block");
            this.students4page = [];
            this.nowpage = 1;
            this.allpage = 1;
            this.deletestu = [];
            this.apply_id = '';
            this.username = '';
            this.identy_card_number = '';
            this.sexpicked = 'option1';
            this.id_ok = 0;
            this.id_error = 0;
            this.name_ok = 0;
            this.name_error = 0;
            this.number_ok = 0;
            this.number_error = 0;
            $("#check_all").prop("checked", false);
            this.$http.get('/admin/students?nowpage=' + page).then(function(response) {
                this.resetstudents4page(response.data);
                //关闭遮罩
                $("#zhezhao").css("display", "none");
                if (is_alert) {
                    alert('刷新成功!学员信息已经更新!');
                }
            }, function() {
                //关闭遮罩
                $("#zhezhao").css("display", "none");
                alert('服务器异常!');
            });
        },

        //获取用户报名号
        get_apply_id: function() {
            var deletestus = this.deletestus; // <-- storing the variable here
            return function() {
                //如果被选中
                if ($(this).prop("checked")) {
                    deletestus.push($(this).parent().parent().children().eq(1).text());
                }
            }
        },

        //获取用户报名号
        clean_mymodel: function() {
            this.apply_id = '';
            this.username = '';
            this.identy_card_number = '';
            this.sexpicked = 'option1';
            this.id_ok = 0;
            this.id_error = 0;
            this.name_ok = 0;
            this.name_error = 0;
            this.number_ok = 0;
            this.number_error = 0;
            return function() {}
        },

        //删除学员信息
        deletestu: function() {
            //启动遮罩
            $("#zhezhao").css("display", "block");
            //遍历所有li
            $(".check_cld").each(
                this.get_apply_id()
            );
            if (this.deletestus.length > 0) {
                postdata = {
                    'deletestus': this.deletestus
                };
                this.$http.post('/admin/students/del', postdata).then(function(response) {
                    //关闭遮罩
                    $("#zhezhao").css("display", "none");
                    if (response.data.code == 200) {
                        // 清空
                        this.deletestus = [];
                        alert('删除成功!学员信息已经更新!');
                        //刷新学员信息
                        this.refreshstu();
                    } else {
                        alert('服务器异常!');
                    }
                }, function() {
                    //关闭遮罩
                    $("#zhezhao").css("display", "none");
                    alert('服务器异常!');
                });
            } else {
                //关闭遮罩
                $("#zhezhao").css("display", "none");
                alert("请选择至少一位学员!");
            }
        }
    }
})
