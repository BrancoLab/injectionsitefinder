
# --------------------- reconstruct surface of injection --------------------- #

scene = CellFinderScene(add_root=False)

# Define target and param
target_region = 'SCm'
target_hemisphere = 'left'
max_distance_from_target = 2000

# Get target region COM
target_com = scene.get_region_CenterOfMass(target_region, unilateral=False) # hemisphere=target_hemisphere)


# Get cells within distance from com
cells_coords = [(r.x, r.y, r.z) for i,r in ch0_cells.iterrows()]
cells_com_distances = [euclidean(target_com, p) for p in cells_coords]
cells_in_range = [c for c,d in zip(cells_coords, cells_com_distances) if d <= max_distance_from_target]


# Get biggest cluster
clusters = cluster(cells_in_range, 100)
n_cells_in_cluster = [len(c) for c in clusters.info['clusters']]
idxs = np.argsort(n_cells_in_cluster)
clusters = [clusters.info['clusters'][i] for i in idxs][::-1]

cells_to_exclude = Points(removeOutliers(clusters[0], 70))
hull = convexHull(cells_to_exclude).alpha(.5).color('salmon')


# injection = splitByConnectivity(cells_to_exclude)[-1]


# Render
scene.add_vtkactor(cells_to_exclude)
scene.add_vtkactor(hull)

scene.add_brain_regions(['SCm'], use_original_color=True, wireframe=True, alpha=.5)
scene.render()