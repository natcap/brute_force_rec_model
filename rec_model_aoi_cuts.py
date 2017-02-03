"""Go feature by feature for recreation model."""
import os

from osgeo import ogr
import natcap.invest.recreation.recmodel_client


def main():
    """Entry point."""
    workspace_dir = r"rec_model_aoi_cuts_workspace"
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
    aoi_path = r"C:\Users\rpsharp\Downloads\AdminForest (1)\AdminForest.shp"
    aoi_vector = ogr.Open(aoi_path)
    aoi_layer = aoi_vector.GetLayer()
    driver = ogr.GetDriverByName("ESRI Shapefile")
    fid_list = []
    for aoi_feature in aoi_layer:
        aoi_fid = aoi_feature.GetFID()
        fid_list.append(aoi_fid)
        print aoi_fid

        target_vector_path = os.path.join(
            workspace_dir, "%d_feature.shp" % aoi_fid)

        # Remove output shapefile if it already exists
        if os.path.exists(target_vector_path):
            driver.DeleteDataSource(target_vector_path)

        # Create the output shapefile
        target_vector = driver.CreateDataSource(target_vector_path)
        target_layer = target_vector.CreateLayer(
            "%d_feature" % aoi_fid,
            aoi_layer.GetSpatialRef(), ogr.wkbPolygon)
        target_layer.CreateFeature(aoi_feature)
        target_layer = None
        target_vector = None

        args = {
            'aoi_path': target_vector_path,
            'compute_regression': False,
            'grid_aoi': False,
            'results_suffix': "%d_feature" % aoi_fid,
            'start_year': '2005',
            'end_year': '2014',
            'workspace_dir': workspace_dir,
        }
        natcap.invest.recreation.recmodel_client.execute(args)

    # combine the resulting shapefiles into one big one
    source_aoi_path = os.path.join(
        workspace_dir, "pud_results_%d_feature.shp" % fid_list[0])
    source_vector = ogr.Open(source_aoi_path)
    target_aoi_path = os.path.join(workspace_dir, os.path.basename(aoi_path))
    if os.path.exists(target_aoi_path):
        os.remove(target_aoi_path)
    target_aoi_vector = driver.CopyDataSource(source_vector, target_aoi_path)
    source_vector = None
    target_aoi_layer = target_aoi_vector.GetLayer()
    for fid in fid_list[1::]:
        source_path = os.path.join(
            workspace_dir, "pud_results_%d_feature.shp" % fid)
        source_vector = ogr.Open(source_path)
        source_layer = source_vector.GetLayer()
        # this loop will only hit once, but is a convenient way to get the
        # feature without guessing as to its internal FID even though it
        # probably is 0.
        for source_feature in source_layer:
            # reset the FID field that's set on the server
            source_feature.SetField("FID", fid)
            target_aoi_layer.CreateFeature(source_feature)
        source_layer = None
        source_vector = None

    # combine table results
    table_path = os.path.join(workspace_dir, 'monthly_table.csv')
    header_printed = False
    with open(table_path, 'wb') as table_file:
        for fid in fid_list:
            feature_table_path = os.path.join(
                workspace_dir, 'monthly_table_%d_feature.csv' % fid)
            with open(feature_table_path) as feature_table:
                if header_printed:
                    feature_table.readline()  # discard header
                else:
                    table_file.write(feature_table.readline())
                    header_printed = True
                poly_line = feature_table.readline().split(',')
                poly_line[0] = str(fid)
                table_file.write(','.join(poly_line))

    # delete the no longer needed result polygons
    for fid in fid_list:
        source_path = os.path.join(
            workspace_dir, "pud_results_%d_feature.shp" % fid)
        driver.DeleteDataSource(source_path)
        source_path = os.path.join(
            workspace_dir, "%d_feature.shp" % fid)
        driver.DeleteDataSource(source_path)
        source_path = os.path.join(
            workspace_dir, "monthly_table_%d_feature.csv" % fid)
        os.remove(source_path)

if __name__ == '__main__':
    main()
