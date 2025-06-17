# better-ros2-bag-record

The usual ros2 bag record doesn't save params. But it was important to me. Since all params are associated with each node, ping each value of the params while the nodes are running is very inefficient. But the params (at runtime) are read from the install folder. This script does ros2 bag record, reads the config files (.yaml) in the user-defined packages and stores the all the params in a single file in the location where the bag is stored.
<br>
<br>
Change Line 29,21 to the respective workspace name and the packages whose config files (.yaml) you'd want to be saved alongside the ROS bag
