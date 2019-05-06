package com.ljm.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

@Controller
@RequestMapping("/analyser")
public class analyserController {

    @RequestMapping("/test")
    @ResponseBody
    public String getPythonProcedure(String weiboId){
        System.out.println("爬取的微博ID："+ weiboId);

        //数据爬取
        String exe ="python";
        String command = "D:/Desktop/Desktop/GraduationDesign/weboSpider.py";
        String[] cmdArr = new String[]{exe, command, weiboId};
        try {
            Process pr = Runtime.getRuntime().exec(cmdArr);
            BufferedReader in = new BufferedReader(new InputStreamReader(
                    pr.getInputStream(),"gbk"));
            String line;
            System.out.println("正在抓取微博微博数据，请稍后...");
            while ((line = in.readLine()) != null) {
                System.out.println(line);
                if(line.equals("error")){
                    System.out.println("微博ID错误，请重新输入！");
                    return "failed";
                }
            }
            in.close();
            pr.waitFor();
        } catch (Exception e) {
            e.printStackTrace();
        }

        String command2 = "D:/Desktop/Desktop/GraduationDesign/trainModel_dic.py";
        String[] cmdArr2 = new String[]{exe, command2, weiboId};
        try {
            System.out.println("正在对数据进行分析...");
            Process pr = Runtime.getRuntime().exec(cmdArr2);
            BufferedReader in = new BufferedReader(new InputStreamReader(
                    pr.getInputStream(),"gbk"));
            String line;


            while ((line = in.readLine()) != null) {
                System.out.println(line);
            }
            System.out.println("数据分析完成");
            in.close();
            pr.waitFor();
        } catch (Exception e) {
            e.printStackTrace();
        }

        return "success";
    }

}
