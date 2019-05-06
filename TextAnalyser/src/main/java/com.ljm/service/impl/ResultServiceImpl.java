package com.ljm.service.impl;


import com.ljm.dao.ResultDao;

import com.ljm.model.Result;
import com.ljm.service.ResultService;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.List;

@Service("resultService")
public class ResultServiceImpl implements ResultService {

    @Resource
    private ResultDao resultDao;

    @Override
    public List<Result> getResultList() {
        return this.resultDao.getResult();
    }
}