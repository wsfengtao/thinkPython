Vue.config.delimiters = ['${', '}']

// 查询数据模型
var LoginModel = new Vue({
    el: '#login4Index',
    data: {
        number: '',
        username: '',
        backname: '',
        backnumber: '',
        backfenshu: ''
    },
    methods: {
        search: function() {
            search_data = {
                number: this.number,
                username: this.username
            };
            var s_number = /\d{8}/;
            var s_username = /[\u4E00-\u9FA5]{2,4}/;
            if (!s_number.test(this.number) || this.number.length != 8) {
                alert('考生号必须为8位数字!');
            } else if (!s_username.test(this.username) || this.username.length > 4) {
                alert('请输入正确格式的姓名!');
            } else {
                //启动遮罩
                $("#zhezhao").css("display", "block");
                this.$http.post('/army/search', search_data).then(function(response) {
                    if (response.data.code == 200) {
                        $("#search4Index").hide();
                        alert('查询成功!');
                        this.backname = response.data.username;
                        this.backnumber = response.data.number;
                        this.backfenshu = response.data.fenshu;
                        $("#show4Index").show();
                        //关闭遮罩
                        $("#zhezhao").css("display", "none");
                    } else if (response.data.code == 501) {
                        alert('考生号或姓名不能为空!');
                        //关闭遮罩
                        $("#zhezhao").css("display", "none");
                    } else if (response.data.code == 500) {
                        alert('考生号或姓名不正确!');
                        //关闭遮罩
                        $("#zhezhao").css("display", "none");
                    }
                }, function() {
                    //关闭遮罩
                    $("#zhezhao").css("display", "none");
                    alert('服务器异常!');
                });
            }
        },
        backtosearch: function() {
            //启动遮罩
            $("#zhezhao").css("display", "block");
            this.number = '';
            this.username = '';
            this.backname = '';
            this.backnumber = '';
            this.fenshu = '';
            $("#search4Index").show();
            $("#show4Index").hide();
            //关闭遮罩
            $("#zhezhao").css("display", "none");
        }
    }
})
