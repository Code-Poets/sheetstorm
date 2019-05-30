### next


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
