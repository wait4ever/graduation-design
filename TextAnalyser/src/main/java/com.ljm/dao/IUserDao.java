package com.ljm.dao;

import com.ljm.model.User;

public interface IUserDao {

    User selectUser(long id);

}