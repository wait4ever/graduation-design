package com.ljm.controller;

import com.ljm.model.Result;
import com.ljm.service.ResultService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import javax.annotation.Resource;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

@Controller
@RequestMapping("/result")
public class resultController {
    @Resource
    private ResultService resultService;

    @RequestMapping("/history")
    public String getPythonProcedure(){
        return "resultInfo";
    }

    @ResponseBody
    @RequestMapping("/data")
    public List<Result> GetDepartment(ModelMap modelMap) {
        List<Result> resultList;
        resultList = resultService.getResultList();
        System.out.println(resultList);
        return resultList;
    }

    @RequestMapping("/detail")
    public String GetDetail(String weiboId) {
        System.out.println(weiboId);
        return "resultDetail";
    }

}
