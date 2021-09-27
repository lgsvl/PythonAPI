#
# Copyright (c) 2021 LG Electronics, Inc.
#
# This software contains code licensed as described in LICENSE.
#


# Settings classes with common variables used in the quickstart and example scripts.
class SimulatorSettings:
    # IP address of the endpoint running the Simulator. Default value is "127.0.0.1"
    simulator_host = "127.0.0.1"

    # Port used by the Simulator for the Python API connection. Default value is 8181
    simulator_port = 8181

    # IP address of the endpoint running the bridge. Default value is "127.0.0.1"
    bridge_host = "127.0.0.1"

    # Port used by the Simulator for the bridge connection. Default value is 9090
    bridge_port = 9090


class DefaultAssets:
    # Map loaded in the quickstart scripts. Changing the map may lead to unexpected behaviour in the quickstart scripts. Default value is "BorregasAve".
    # https://wise.svlsimulator.com/maps/profile/aae03d2a-b7ca-4a88-9e41-9035287a12cc
    map_borregasave = "aae03d2a-b7ca-4a88-9e41-9035287a12cc"

    # Map loaded in the quickstart scripts. Changing the map may lead to unexpected behaviour in the quickstart scripts. Default value is "CubeTown".
    # https://wise.svlsimulator.com/maps/profile/06773677-1ce3-492f-9fe2-b3147e126e27
    map_cubetown = "06773677-1ce3-492f-9fe2-b3147e126e27"

    # Map loaded in some of the examples. Changing the map may lead to unexpected behaviour in the example scripts. Default value is "SanFrancisco".
    # https://wise.svlsimulator.com/maps/profile/5d272540-f689-4355-83c7-03bf11b6865f
    map_sanfrancisco = "5d272540-f689-4355-83c7-03bf11b6865f"

    # Map loaded in some of the examples. Changing the map may lead to unexpected behaviour in the example scripts. Default value is "Straight1LanePedestrianCrosswalk".
    # https://wise.svlsimulator.com/maps/profile/a3a818b5-c66b-488a-a780-979bd5692db1
    map_straight1lanepedestriancrosswalk = "a3a818b5-c66b-488a-a780-979bd5692db1"

    # Map loaded in some of the examples. Changing the map may lead to unexpected behaviour in the example scripts. Default value is "SingleLaneRoad".
    # https://wise.svlsimulator.com/maps/profile/a6e2d149-6a18-4b83-9029-4411d7b2e69a
    map_singlelaneroad = "a6e2d149-6a18-4b83-9029-4411d7b2e69a"

    # Map loaded in some of the examples. Changing the map may lead to unexpected behaviour in the example scripts. Default value is "Straight1LaneSame".
    # https://wise.svlsimulator.com/maps/profile/1e2287cf-c590-4804-bcb1-18b2fd3752d1
    map_straight1lanesame = "1e2287cf-c590-4804-bcb1-18b2fd3752d1"

    # Map loaded in some of the examples. Changing the map may lead to unexpected behaviour in the example scripts. Default value is "Straight2LaneSame".
    # https://wise.svlsimulator.com/maps/profile/b39d3ef9-21d7-409d-851b-4c90dad80a25
    map_straight2lanesame = "b39d3ef9-21d7-409d-851b-4c90dad80a25"

    # Map loaded in some of the examples. Changing the map may lead to unexpected behaviour in the example scripts. Default value is "Straight2LaneSameCurbRightIntersection".
    # https://wise.svlsimulator.com/maps/profile/378edc3f-8fce-4596-87dc-7d12fc2ad743
    map_straight2lanesamecurbrightintersection = "378edc3f-8fce-4596-87dc-7d12fc2ad743"

    # Map loaded in some of the examples. Changing the map may lead to unexpected behaviour in the example scripts. Default value is "Straight2LaneOpposing".
    # https://wise.svlsimulator.com/maps/profile/671868be-44f9-44a1-913c-cb0f29d12634
    map_straight2laneopposing = "671868be-44f9-44a1-913c-cb0f29d12634"

    # Map loaded in the quickstart scripts. Changing the map may lead to unexpected behaviour in the quickstart scripts. Default value is "LGSeocho".
    # https://wise.svlsimulator.com/maps/profile/26546191-86e8-4b53-9432-1cecbbd95c87
    map_lgseocho = "26546191-86e8-4b53-9432-1cecbbd95c87"

    # Ego vehicle that is loaded in most of the quickstart scripts. Default value is "Lincoln2017MKZ" using the "Apollo 5.0" sensor configuration.
    # This includes a bridge connection if needed and also bunch of sensors including LIDAR.
    # https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e/edit/configuration/47b529db-0593-4908-b3e7-4b24a32a0f70
    ego_lincoln2017mkz_apollo5 = "47b529db-0593-4908-b3e7-4b24a32a0f70"

    # Ego vehicle that is loaded in quickstart/tests scripts. Default value is "Jaguar2015XE" using the "Apollo 5.0" sensor configuration.
    # https://wise.svlsimulator.com/vehicles/profile/3f4211dc-e5d7-42dc-94c5-c4832b1331bb/edit/configuration/c06d4932-5928-4730-8a91-ba64ac5f1813
    ego_jaguar2015xe_apollo5 = "c06d4932-5928-4730-8a91-ba64ac5f1813"

    # Ego vehicle that is loaded in quickstart/tests scripts. Default value is "Jaguar2015XE" using the "Autoware AI" sensor configuration.
    # https://wise.svlsimulator.com/vehicles/profile/3f4211dc-e5d7-42dc-94c5-c4832b1331bb/edit/configuration/05cbb194-d095-4a0e-ae66-ff56c331ca83
    ego_jaguae2015xe_autowareai = "05cbb194-d095-4a0e-ae66-ff56c331ca83"

    # Ego vehicle that is loaded in most of the NHTSA example scripts. Default value is "Lincoln2017MKZ" using the "Apollo 5.0 (Full Analysis)" sensor configuration.
    # This includes bunch of sensors that help analyze test results efficiently.
    # https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e/edit/configuration/22656c7b-104b-4e6a-9c70-9955b6582220
    ego_lincoln2017mkz_apollo5_full_analysis = "22656c7b-104b-4e6a-9c70-9955b6582220"

    # Ego vehicle that is loaded in most of the NHTSA example scripts. Default value is "Lincoln2017MKZ" using the "Apollo 5.0 (modular testing)" sensor configuration.
    # This has sensors for modular testing.
    # https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e/edit/configuration/5c7fb3b0-1fd4-4943-8347-f73a05749718
    ego_lincoln2017mkz_apollo5_modular = "5c7fb3b0-1fd4-4943-8347-f73a05749718"

    # Ego vehicle that is loaded in most of the Apollo 6.0 scripts. Default value is "Lincoln2017MKZ" using the "Apollo 6.0 (modular testing)" sensor configuration.
    # This has sensors for modular testing.
    # https://wise.svlsimulator.com/vehicles/profile/73805704-1e46-4eb6-b5f9-ec2244d5951e/edit/configuration/2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921
    ego_lincoln2017mkz_apollo6_modular = "2e9095fa-c9b9-4f3f-8d7d-65fa2bb03921"

    # Cloi robot that is loaded in quickstart/tests scripts. Default value is "LGCloi" using the "Navigation2" sensor configuration.
    # https://wise.svlsimulator.com/vehicles/profile/20609b67-6dbd-40ad-9b46-e6bc455278ed/edit/configuration/c2207cd4-c8d0-4a12-b5b7-c79ab748becc
    ego_lgcloi_navigation2 = "c2207cd4-c8d0-4a12-b5b7-c79ab748becc"

    # Cloi robot that is loaded in quickstart/tests scripts. Default value is "LGCloi" using the "Nav2_Multi_Robot1" sensor configuration.
    # https://wise.svlsimulator.com/vehicles/profile/20609b67-6dbd-40ad-9b46-e6bc455278ed/edit/configuration/eee61d18-c6e3-4292-988d-445802aaee97
    ego_lgcloi_navigation2_multi_robot1 = "eee61d18-c6e3-4292-988d-445802aaee97"

    # Cloi robot that is loaded in quickstart/tests scripts. Default value is "LGCloi" using the "Nav2_Multi_Robot2" sensor configuration.
    # https://wise.svlsimulator.com/vehicles/profile/20609b67-6dbd-40ad-9b46-e6bc455278ed/edit/configuration/f9c5ace0-969a-4ade-8208-87d09d1a53f8
    ego_lgcloi_navigation2_multi_robot2 = "f9c5ace0-969a-4ade-8208-87d09d1a53f8"

    # Cloi robot that is loaded in quickstart/tests scripts. Default value is "LGCloi" using the "Nav2_Multi_Robot3" sensor configuration.
    # https://wise.svlsimulator.com/vehicles/profile/20609b67-6dbd-40ad-9b46-e6bc455278ed/edit/configuration/cfdb1484-91b7-4f27-b729-e313cc31ed8e
    ego_lgcloi_navigation2_multi_robot3 = "cfdb1484-91b7-4f27-b729-e313cc31ed8e"
