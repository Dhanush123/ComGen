b'package threadPoolExecutor;\n\nimport java.util.Date;\n\n/**\n * \xe8\xbf\x99\xe6\x98\xaf\xe4\xb8\x80\xe4\xb8\xaa\xe7\xae\x80\xe5\x8d\x95\xe7\x9a\x84Runnable\xe7\xb1\xbb\xef\xbc\x8c\xe9\x9c\x80\xe8\xa6\x81\xe5\xa4\xa7\xe7\xba\xa65\xe7\xa7\x92\xe9\x92\x9f\xe6\x9d\xa5\xe6\x89\xa7\xe8\xa1\x8c\xe5\x85\xb6\xe4\xbb\xbb\xe5\x8a\xa1\xe3\x80\x82\n * @author shuang.kou\n */\npublic class MyRunnable implements Runnable {\n\n    private String command;\n\n    public MyRunnable(String s) {\n        this.command = s;\n    }\n\n    @Override\n    public void run() {\n        System.out.println(Thread.currentThread().getName() + " Start. Time = " + new Date());\n        processCommand();\n        System.out.println(Thread.currentThread().getName() + " End. Time = " + new Date());\n    }\n\n    private void processCommand() {\n        try {\n            Thread.sleep(5000);\n        } catch (InterruptedException e) {\n            e.printStackTrace();\n        }\n    }\n\n    @Override\n    public String toString() {\n        return this.command;\n    }\n}\n'