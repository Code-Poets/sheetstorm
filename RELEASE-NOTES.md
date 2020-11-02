### v0.12.4

##### Bugfixes

- Bugfix failing users views tests ([#568](https://github.com/Code-Poets/sheetstorm/pull/568))
- Bugfix delete integrity keys in non tags scripts ([#575](https://github.com/Code-Poets/sheetstorm/pull/575))



### v0.12.3

##### Bugfixes

- Bugfix bad padding in report form ([#564](https://github.com/Code-Poets/sheetstorm/pull/564))



### v0.12.2

##### Bugfixes

- Bugfix default date on report creation ([#563](https://github.com/Code-Poets/sheetstorm/pull/563))



### v0.12.1

##### Bugfixes

- Bugfix incorrect hours stats ([#559](https://github.com/Code-Poets/sheetstorm/pull/559))
- Bugfix add process limit for pipenv ([#560](https://github.com/Code-Poets/sheetstorm/pull/560))



### v0.12.0

##### Features

- Feature change ordering in employees' list ([#557](https://github.com/Code-Poets/sheetstorm/pull/557))
- Feature add summary to project report list ([#558](https://github.com/Code-Poets/sheetstorm/pull/558))
- Feature refactor password change view ([#527](https://github.com/Code-Poets/sheetstorm/pull/527))
- Feature add update view for account details ([#506](https://github.com/Code-Poets/sheetstorm/pull/506))

##### Bugfixes

- Bugfix monthly hour stats display ([#556](https://github.com/Code-Poets/sheetstorm/pull/556))



### v0.11.0

##### Features

- Feature refactor project create view ([#513](https://github.com/Code-Poets/sheetstorm/pull/513))
- Feature improve sidebar responsiveness ([#515](https://github.com/Code-Poets/sheetstorm/pull/515))
- Feature rebuild notifications interface ([#541](https://github.com/Code-Poets/sheetstorm/pull/541))
- Feature improve monthly hours stats ([#552](https://github.com/Code-Poets/sheetstorm/pull/552))
- Feature delete whitelisting admin panel ([#555](https://github.com/Code-Poets/sheetstorm/pull/555))
- Feature refactor project reports list view ([#520](https://github.com/Code-Poets/sheetstorm/pull/520))
- Feature tunning nginx for performance ([#539](https://github.com/Code-Poets/sheetstorm/pull/539))

##### Bugfixes

- Bugfix inactive users are displayed in app ([#553](https://github.com/Code-Poets/sheetstorm/pull/553))
- Bugfix readme typo "deafult" ([#554](https://github.com/Code-Poets/sheetstorm/pull/554))
- Bugfix redirect admin to his own report edition ([#543](https://github.com/Code-Poets/sheetstorm/pull/543))
- Bugfix add linebreaks filter to reports description ([#542](https://github.com/Code-Poets/sheetstorm/pull/542))
- Bugfix remove formulas from hours fields ([#537](https://github.com/Code-Poets/sheetstorm/pull/537))



### v0.10.1

##### Bugfixes

- Bugfix illigal characters from description ([#548](https://github.com/Code-Poets/sheetstorm/pull/548))



### v0.10.0

##### Features

- Feature add separate admin endpoint with whitelist of ip addresses ([#534](https://github.com/Code-Poets/sheetstorm/pull/534))
- Feature refactor author report list view ([#517](https://github.com/Code-Poets/sheetstorm/pull/517))
- Feature tunning nginx for performance ([#539](https://github.com/Code-Poets/sheetstorm/pull/539))

##### Bugfixes

- Bugfix completed and suspended projects ([#522](https://github.com/Code-Poets/sheetstorm/pull/522))
- Bugfix hide create project for managers ([#536](https://github.com/Code-Poets/sheetstorm/pull/536))



### v0.9.0

##### Features

- Feature add dynamic filter for task activities per project ([#469](https://github.com/Code-Poets/sheetstorm/pull/469))
- Feature add option to switch off notifications ([#483](https://github.com/Code-Poets/sheetstorm/pull/483))
- Feature add top border to separate days in excel reports ([#481](https://github.com/Code-Poets/sheetstorm/pull/481))
- Feature export csv for project as one file ([#474](https://github.com/Code-Poets/sheetstorm/pull/474))
- Feature project should have customisable task activity list ([#460](https://github.com/Code-Poets/sheetstorm/pull/460))
- Feature rebuild user reports interface ([#312](https://github.com/Code-Poets/sheetstorm/pull/312))
- Feature refactor project list template view ([#508](https://github.com/Code-Poets/sheetstorm/pull/508))
- Feature remove fields due to rodo ([#516](https://github.com/Code-Poets/sheetstorm/pull/516))

##### Bugfixes

- Bugfix disable `cyclic-import` in pylintrc config ([#500](https://github.com/Code-Poets/sheetstorm/pull/500))
- Bugfix incorrect display of reports ([#486](https://github.com/Code-Poets/sheetstorm/pull/486))
- Bugfix managers field in project admin form ([#472](https://github.com/Code-Poets/sheetstorm/pull/472))
- Bugfix remove task activity from project ([#503](https://github.com/Code-Poets/sheetstorm/pull/503))
- Bugfix scripts and links security vulnerabilities ([#528](https://github.com/Code-Poets/sheetstorm/pull/528))
- Bugfix stop_date and suspended field in project ([#505](https://github.com/Code-Poets/sheetstorm/pull/505))



### v0.8.0

##### Features

- Feature add export to project author report project view ([#424](https://github.com/Code-Poets/sheetstorm/pull/424))
- Feature add lines separators in columns ([#439](https://github.com/Code-Poets/sheetstorm/pull/439))
- Feature add notifications ([#421](https://github.com/Code-Poets/sheetstorm/pull/421))
- Feature enable export reports to csv file ([#326](https://github.com/Code-Poets/sheetstorm/pull/326))
- Feature improve managers and employees selection ([#416](https://github.com/Code-Poets/sheetstorm/pull/416))

##### Bugfixes

- Bugfix add set method for printing ([#426](https://github.com/Code-Poets/sheetstorm/pull/426))
- Bugfix add freeze_time decorator to work percentage time mixin tests ([#465](https://github.com/Code-Poets/sheetstorm/pull/465))
- Bugfix add task activities to Report in initial data ([#450](https://github.com/Code-Poets/sheetstorm/pull/450))
- Bugfix change "Recent month" to "Current month" in month navigation bar ([#429](https://github.com/Code-Poets/sheetstorm/pull/429))
- Bugfix change CustomUser's manager to enable migration making ([#451](https://github.com/Code-Poets/sheetstorm/pull/451))
- Bugfix change name from 'My Reports' to 'Reports' ([#455](https://github.com/Code-Poets/sheetstorm/pull/455))
- Bugfix custom report list ([#446](https://github.com/Code-Poets/sheetstorm/pull/446))
- Bugfix login and home urls ([#438](https://github.com/Code-Poets/sheetstorm/pull/438))
- Bugfix failing  tests in master ([#470](https://github.com/Code-Poets/sheetstorm/pull/470))
- Bugfix modify template to preserve user's email in case of errors ([#467](https://github.com/Code-Poets/sheetstorm/pull/467))
- Bugfix month navigation ([#466](https://github.com/Code-Poets/sheetstorm/pull/466))
- Bugfix navigation form (in case of malformed date) ([#471](https://github.com/Code-Poets/sheetstorm/pull/471))
- Bugfix OpenOffice does not display full description ([#423](https://github.com/Code-Poets/sheetstorm/pull/423))
- Bugfix set active actual url ([#448](https://github.com/Code-Poets/sheetstorm/pull/448))
- Bugfix stats at the bottom of report list should involve reports from last 30 days ([#419](https://github.com/Code-Poets/sheetstorm/pull/419))
- Bugfix total hours in csv in project reports ([#440](https://github.com/Code-Poets/sheetstorm/pull/440))
- Bugfix urls namespace and add reverse to missing usages in tests ([#428](https://github.com/Code-Poets/sheetstorm/pull/428))
- Bugfix weekends should be skipped in reports date suggestion ([#427](https://github.com/Code-Poets/sheetstorm/pull/427))
- Bugfix work hours display in report update ([#417](https://github.com/Code-Poets/sheetstorm/pull/417))



### v0.7.4

##### Bugfixes

- Bugfix add auto assigning manager if he create project ([#390](https://github.com/Code-Poets/sheetstorm/pull/390))
- Bugfix change names in UI ([#385](https://github.com/Code-Poets/sheetstorm/pull/385))
- Bugfix disable mounting additional disk on the local virtual machine ([#389](https://github.com/Code-Poets/sheetstorm/pull/389))
- Bugfix fill context on invalid form response ([#379](https://github.com/Code-Poets/sheetstorm/pull/379))
- Bugfix missing work hours during updating reports ([#384](https://github.com/Code-Poets/sheetstorm/pull/384))


### v0.7.3

##### Features

- Feature add automatically creating and mounting an additional disk for postgression backup purposes ([#373](https://github.com/Code-Poets/sheetstorm/pull/373))

##### Bugfixes

- Bugfix add more restrict setting work_hours value ([#378](https://github.com/Code-Poets/sheetstorm/pull/378))
- Bugfix add validation for special characters in names ([#381](https://github.com/Code-Poets/sheetstorm/pull/381))
- Bugfix for on report editing, the task activity is set to default ([#377](https://github.com/Code-Poets/sheetstorm/pull/377))
- Bugfix variable default date value on report creation ([#375](https://github.com/Code-Poets/sheetstorm/pull/375))


### v0.7.2

##### Bugfixes

- Bugfix "---------------" in projects dropdown list in reposr list view ([#349](https://github.com/Code-Poets/sheetstorm/pull/349))
- Bugfix regex for extracting year and month from url ([#364](https://github.com/Code-Poets/sheetstorm/pull/364))


### v0.7.1

##### Bugfixes

- Bugfix calendar widget display in `report-list` ([#357](https://github.com/Code-Poets/sheetstorm/pull/357))


### v0.7.0

##### Features

- Feature add day name to reports ([#346](https://github.com/Code-Poets/sheetstorm/pull/346))
- Feature add mask for work hours field in reports form ([#345](https://github.com/Code-Poets/sheetstorm/pull/345))
- Feature add nginx endpoint that allows downloading encrypted postgres backups ([#353](https://github.com/Code-Poets/sheetstorm/pull/353))
- Feature default project for new report ([#327](https://github.com/Code-Poets/sheetstorm/pull/327))
- Feature default task activity for new report ([#337](https://github.com/Code-Poets/sheetstorm/pull/337))
- Feature percentage time of worker for each project ([#330](https://github.com/Code-Poets/sheetstorm/pull/330))

##### Bugfixes

- Bugfix move directives that configure modsecurity nginx module to another place in the nginx config files ([#347](https://github.com/Code-Poets/sheetstorm/pull/347))
- Bugfix MultipleObjectsReturned exception when manager wants to edit his reports ([#354](https://github.com/Code-Poets/sheetstorm/pull/354))


### v0.6.0

##### Features

- Feature add captcha to registration view ([#317](https://github.com/Code-Poets/sheetstorm/pull/317))
- Feature add cron job that automatically renew Let's Encrypt Certificate ([#324](https://github.com/Code-Poets/sheetstorm/pull/324))
- Feature add encryption to postgres backups ([#339](https://github.com/Code-Poets/sheetstorm/pull/339))
- Feature add modsecurity lib to the nginx ([#320](https://github.com/Code-Poets/sheetstorm/pull/320))
- Feature add possibility to export monthly reports for every user ([#332](https://github.com/Code-Poets/sheetstorm/pull/332))
- Feature add signup email confirmation ([#308](https://github.com/Code-Poets/sheetstorm/pull/308))
- Feature better export of reports ([#331](https://github.com/Code-Poets/sheetstorm/pull/331))
- Feature mitigating DDoS attack with nginx ([#297](https://github.com/Code-Poets/sheetstorm/pull/297))
- Feature rebuild register interface ([#283](https://github.com/Code-Poets/sheetstorm/pull/283))

##### Bugfixes

- Bugfix add a missing file that allows you to reset database in the virtual machine ([#338](https://github.com/Code-Poets/sheetstorm/pull/338))
- Bugfix calendar display in user report edit form ([#300](https://github.com/Code-Poets/sheetstorm/issues/300))
- Bugfix change dipslay of `user_type` to be human readable ([#293](https://github.com/Code-Poets/sheetstorm/pull/293))
- Bugfix exporting report description to xls ([#303](https://github.com/Code-Poets/sheetstorm/pull/303))
- Bugfix for incorrect html tag ([#328](https://github.com/Code-Poets/sheetstorm/pull/328))
- Bugfix hide toggle button ([#335](https://github.com/Code-Poets/sheetstorm/pull/335))
- Bugfix make hyperlink highlighted ([#334](https://github.com/Code-Poets/sheetstorm/pull/334))
- Bugfix manager can't edit his own reports in projects where he is not manager ([#319](https://github.com/Code-Poets/sheetstorm/pull/319))
- Bugfix navigation bar ([#322](https://github.com/Code-Poets/sheetstorm/pull/322))
- Bugfix pass markdown_description property to template ([#305](https://github.com/Code-Poets/sheetstorm/pull/305))
- Bugfix update `Django` to `2.2.2` and adapt test ([#302](https://github.com/Code-Poets/sheetstorm/pull/302))


### v0.5.0

##### Features

- Feature access permissions ([#230](https://github.com/Code-Poets/sheetstorm/pull/230))
- Feature automatic deployment process for Sheet Storm ([#273](https://github.com/Code-Poets/sheetstorm/pull/273), [#269](https://github.com/Code-Poets/sheetstorm/pull/269), [#271](https://github.com/Code-Poets/sheetstorm/pull/271), [#270](https://github.com/Code-Poets/sheetstorm/pull/270))
- Feature group days and add daily hours to xlsx export ([#276](https://github.com/Code-Poets/sheetstorm/pull/276))
- Feature month segregation for author report list ([#256](https://github.com/Code-Poets/sheetstorm/pull/256))
- Feature month segregation for project report list ([#138](https://github.com/Code-Poets/sheetstorm/pull/138))
- Feature month segregation for report list ([#139](https://github.com/Code-Poets/sheetstorm/pull/139))

##### Bugfixes

- Bugfix add discard button to admin report detail ([#275](https://github.com/Code-Poets/sheetstorm/pull/275))
- Bugfix add return button in project report list ([#280](https://github.com/Code-Poets/sheetstorm/pull/280))
- Bugfix add validation to stop_date field in project ([#277](https://github.com/Code-Poets/sheetstorm/pull/277))
- Bugfix admin report form ([#263](https://github.com/Code-Poets/sheetstorm/pull/263))
- Bugfix delete button to send it as a post method ([#279](https://github.com/Code-Poets/sheetstorm/pull/279))
- Bugfix generating xlsx for one month ([#230](https://github.com/Code-Poets/sheetstorm/pull/230))
- Bugfix show day numer as non-zero padded decimal ([#265](https://github.com/Code-Poets/sheetstorm/pull/265))
- Bugfix sorting exported reports for project and access permissions ([#266](https://github.com/Code-Poets/sheetstorm/pull/266))


### v0.4.0

##### Features

- Feature add export reports to xlsx ([#212](https://github.com/Code-Poets/sheetstorm/pull/212))

##### Bugfixes

- Bugfix add restriction for non numeric strings to ReportSerializer ([#255](https://github.com/Code-Poets/sheetstorm/pull/255))
- Bugfix add site id fixture ([#260](https://github.com/Code-Poets/sheetstorm/pull/260))
- Bugfix change field type work hours to duration field ([#254](https://github.com/Code-Poets/sheetstorm/pull/254))
- Bugfix converting timedelta to string ([#257](https://github.com/Code-Poets/sheetstorm/pull/257))
- Bugfix creating report in `ReportList` view and adapt test ([#233](https://github.com/Code-Poets/sheetstorm/pull/233))
- Bugfix default creation task activity type during migrations ([#258](https://github.com/Code-Poets/sheetstorm/pull/258))
- Bugfix psycopg requirements ([#249](https://github.com/Code-Poets/sheetstorm/pull/249))


### v0.3.0

##### Features

- Feature adjust templates for printing ([#136](https://github.com/Code-Poets/sheetstorm/pull/136))
- Feature project report detail ([#134](https://github.com/Code-Poets/sheetstorm/pull/134))
- Feature project report list username grouping ([#135](https://github.com/Code-Poets/sheetstorm/pull/135))
- Feature project report list ([#133](https://github.com/Code-Poets/sheetstorm/pull/133))
- Feature sum of hours of reports from a given day lower or euqal to 24 ([#207](https://github.com/Code-Poets/sheetstorm/pull/207))
- Feature hours per day counter ([#137](https://github.com/Code-Poets/sheetstorm/pull/137))
- Feature hours per month counter ([#140](https://github.com/Code-Poets/sheetstorm/pull/140))
- Feature rebuild user interface ([#123](https://github.com/Code-Poets/sheetstorm/pull/123))

##### Bugfixes

- Bugfix 24 hours validation does not work on report creation ([#236](https://github.com/Code-Poets/sheetstorm/pull/236))
- Bugfix add return button on user's report editting screen ([#181](https://github.com/Code-Poets/sheetstorm/pull/181))
- Bugfix add styles to admin report detail ([#180](https://github.com/Code-Poets/sheetstorm/pull/180))
- Bugfix change type annotations for get_reports_created ([#238](https://github.com/Code-Poets/sheetstorm/pull/238))
- Bugfix changed sended pk while editing user in admin update template ([#176](https://github.com/Code-Poets/sheetstorm/pull/179))
- Bugfix disable possibility to change report's author by Admin user ([#201](https://github.com/Code-Poets/sheetstorm/pull/201))
- Bugfix for access to editing managers list and update tests ([#197](https://github.com/Code-Poets/sheetstorm/pull/197))
- Bugfix show all project list ([#237](https://github.com/Code-Poets/sheetstorm/pull/237))
- Bugfix user birth day has no limit ([#231](https://github.com/Code-Poets/sheetstorm/pull/231))
- Bugfix wrong projects displayed after report creation fail ([#228](https://github.com/Code-Poets/sheetstorm/pull/228))


### v0.2.0
- Feature expand description fields character limit ([#177](https://github.com/Code-Poets/sheetstorm/pull/177))
- Bugfix no project selected on join crash ([#168](https://github.com/Code-Poets/sheetstorm/pull/168))
- Bugfix small changes in manager handlers ([#174](https://github.com/Code-Poets/sheetstorm/pull/174))
- Bugfix refactor templates for proper javascript usage ([#169](https://github.com/Code-Poets/sheetstorm/pull/169))
- Fixes to base and js script ([#167](https://github.com/Code-Poets/sheetstorm/pull/167))
- Bugfix repair handlers for admin in handlers ([#165](https://github.com/Code-Poets/sheetstorm/pull/165))
- Bugfix delete button doesn't work for project ([#160](https://github.com/Code-Poets/sheetstorm/pull/160))
- Chore change toggle icon ([#164](https://github.com/Code-Poets/sheetstorm/pull/164))
- Feature admin report detail ([#132](https://github.com/Code-Poets/sheetstorm/pull/132))
- Feature rebuild login interface ([#122](https://github.com/Code-Poets/sheetstorm/pull/122))
- Feature author report list ([#131](https://github.com/Code-Poets/sheetstorm/pull/131))


### v0.1.1
 - Chore adding favicon to app ([#146](https://github.com/Code-Poets/sheetstorm/issues/146))
 - Feature default date input ([#129](https://github.com/Code-Poets/sheetstorm/issues/129))


### v0.1.0
 - User can pick task activity type ([#111](https://github.com/Code-Poets/sheetstorm/issues/111))
 - Description field is ready to prepare reports. ([#106](https://github.com/Code-Poets/sheetstorm/issues/106))
 - Admin is allow to see projects and manage them. ([#85](https://github.com/Code-Poets/sheetstorm/issues/85), [#86](https://github.com/Code-Poets/sheetstorm/issues/86), [#87](https://github.com/Code-Poets/sheetstorm/issues/87), [#88](https://github.com/Code-Poets/sheetstorm/issues/88), [#89](https://github.com/Code-Poets/sheetstorm/issues/89))
 - Manager is allow to see projects and manage his project. ([#85](https://github.com/Code-Poets/sheetstorm/issues/85), [#86](https://github.com/Code-Poets/sheetstorm/issues/86), [#87](https://github.com/Code-Poets/sheetstorm/issues/87), [#88](https://github.com/Code-Poets/sheetstorm/issues/88), [#89](https://github.com/Code-Poets/sheetstorm/issues/89))
 - Add possibility to change user account password. ([#38](https://github.com/Code-Poets/sheetstorm/issues/38))
 - Add mail server ([#38](https://github.com/Code-Poets/sheetstorm/issues/38))
 - Markdown support to description field. ([#37](https://github.com/Code-Poets/sheetstorm/issues/37))
 - Employee are allow to join project. ([#21](https://github.com/Code-Poets/sheetstorm/issues/21))
 - Users are allow to join project. ([#21](https://github.com/Code-Poets/sheetstorm/issues/21))
 - Add accurate hour display. ([#20](https://github.com/Code-Poets/sheetstorm/issues/20))
 - Custom view for users. ([#18](https://github.com/Code-Poets/sheetstorm/issues/18))
 - Create graphical base user interface. ([#18](https://github.com/Code-Poets/sheetstorm/issues/18))
 - Admin is allow to manage employees list. ([#13](https://github.com/Code-Poets/sheetstorm/issues/13))
 - Users are possible to set and change account details. ([#13](https://github.com/Code-Poets/sheetstorm/issues/13))
 - Implement SheetStorm user authentication. ([#6](https://github.com/Code-Poets/sheetstorm/issues/6), [#11](https://github.com/Code-Poets/sheetstorm/issues/11))
