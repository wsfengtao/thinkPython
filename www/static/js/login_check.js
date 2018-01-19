Vue.config.delimiters = ['${', '}']

// 登陆数据模型
var LoginModel = new Vue({
    el: '#login4Index',
    data: {
        account: '',
        password: ''
    },
    methods: {
        login: function() {
            login_data = {
                zhanghu: this.account,
                password: this.password
            };
            this.$http.post('/admin/login', login_data).then(function(response) {
                if (response.data.code == 200) {
                    this.$el.submit();
                } else if (response.data.code == 501) {
                    alert('账户或密码不能为空!');
                } else if (response.data.code == 500) {
                    alert('账户或密码不正确!');
                }
            }, function() {
                alert('服务器异常!');
            });
        }
    }
})
