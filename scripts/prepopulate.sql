truncate table cv_ref.ref_NSPL_postcode_to_lad_code_mapping;
truncate table cv_base.clean_local_area_restrictions;
truncate table cv_ref.ref_ONSUD_uprn_to_lad_code_mapping;

insert into cv_ref.ref_NSPL_postcode_to_lad_code_mapping (pcd, laua, ctry, provisioned_datetime) values 
("BB11TA","E06000008","E92000001" , NOW()), 
("LE674AY", "E07000134","E92000001" , NOW()), 
("L244AD","E06000006" ,"E92000001" , NOW());

insert into cv_base.clean_local_area_restrictions (lad_code, lad_name, alert_level, start_datetime) values
("E06000008", "Blackburn", "4", NOW()),
("E07000134", "Leighton", "3", NOW()),
("E06000006", "Lowestoft", "2", NOW());

insert into cv_ref.ref_ONSUD_uprn_to_lad_code_mapping (uprn, lad19cd, ctry, provisioned_datetime) values 
(1000, "E07000134", "E92000001", NOW() ),
(2000, "E06000006", "E92000001", NOW() ),
(3000, "E09000134", "M83000003", NOW() ),
(10000000, "E06000008", "E92000001", NOW() );
