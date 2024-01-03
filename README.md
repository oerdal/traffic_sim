# Traffic Sim

This project aims to answer many questions about traffic that I ponder while stuck in the notorious LA/OC traffic.

The eventual testing will be approached from a "Mythbusters" perspective, targetting specific hunches such as:

* The slow lane moves faster than the fast lane in rush hour traffic

* Highway patrol are a significant factor in traffic without any stops/arrests being made

* Giving "sufficient room" actually increases traffic

* Speeding up to let a driver merge behind is better than slowing down to let them merge ahead

... and other questions as they appear.

## Current Working Product

![Demo Screenshot](./traffic_sim_demo.png)

Traffic moves across lanes with periodically spawning cars that change lanes occasionally. Contains basic logging functionality to view car numbers and information about specific cars such as their kinematic and simulation information.


## TODO:

* Road merges

* Lights & signs

* Curving roads

* More involved car generation
    * Driver agents
    * Car classes

* Crash/accident logging

* Dynamic speed limits