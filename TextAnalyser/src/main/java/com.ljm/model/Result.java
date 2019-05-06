package com.ljm.model;

import java.util.Date;

public class Result {
    private String weiboId;
    private String status;
    private Date createdTime;

    public String getWeiboId() {
        return weiboId;
    }

    public Date getCreatedTime() {
        return createdTime;
    }

    public String getStatus() {
        return status;
    }

    public void setWeiboId(String weiboId) {
        this.weiboId = weiboId;
    }

    public void setCreatedTime(Date createdTime) {
        this.createdTime = createdTime;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
