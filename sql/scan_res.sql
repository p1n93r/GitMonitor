create table scan_res
(
    sid int auto_increment comment '自增主键'
        primary key,
    url varchar(200) not null comment '结果url',
    count int not null comment '当前查询对应的结果个数'
)
    comment '扫描结果';

