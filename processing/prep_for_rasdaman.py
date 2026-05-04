#!/usr/bin/env python3
"""
Convert string dimensions to integers for Rasdaman ingestion.

This script takes a NetCDF file with string dimensions and converts specified
string dimensions (model, era) to integer indices, storing the original string
mappings in the dimension's attributes as 'encoding'.

This script also forces the variable data to float32 data type for consistency.

Usage:
    python prep_for_rasdaman.py <input_file> <output_file>
"""
import sys
import argparse
from pathlib import Path
import xarray as xr
import numpy as np
import ast


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert string dimensions to integers and set data types for Rasdaman ingestion",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to input NetCDF file with string dimensions"
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="Path for output NetCDF file with integer dimensions"
    )
    parser.add_argument(
        "--string-dims",
        nargs="*",
        default=["model", "era", "source"],
        help="List of string dimensions to convert to integers"
    )
    return parser.parse_args()


def create_encoding_mapping(values):
    # Get unique values and sort them for consistent ordering
    unique_values = sorted(list(set(str(val) for val in values)))
    
    # Create mapping: {index: string_value}
    encoding_map = {i: val for i, val in enumerate(unique_values)}
    
    # Create reverse mapping: {string_value: index}
    reverse_map = {val: i for i, val in enumerate(unique_values)}
    return encoding_map, reverse_map


def convert_variable_dtype(ds, var_name, dtype=np.float32):
    print(f"Converting variable '{var_name}' to data type {dtype}")
    ds[var_name] = ds[var_name].astype(dtype)
    return ds


def convert_string_dimensions(ds, string_dims):    
    # Create a copy of the dataset to modify
    ds_converted = ds.copy()

    # Convert specified string dimensions and populate encoding mappings
    print(f"Converting string dimensions: {string_dims}")
    for dim_name in string_dims:
        if dim_name not in ds.coords:
            print(f"WARNING: Dimension '{dim_name}' not found in dataset, skipping")
            continue
            
        print(f"\nProcessing dimension: {dim_name}")
        
        # Get original string values
        original_values = ds[dim_name].values
        print(f"  Original values: {original_values}")
        print(f"  Original dtype: {ds[dim_name].dtype}")
        
        # Create encoding mapping
        encoding_map, reverse_map = create_encoding_mapping(original_values)
        print(f"  Encoding mapping: {encoding_map}")

        # Convert string values to integer indices
        integer_indices = [reverse_map[str(val)] for val in original_values]
        print(f"  Integer indices: {integer_indices}")
        
        # Update the coordinate with integer values
        ds_converted = ds_converted.assign_coords({
            dim_name: integer_indices
        })

        # Store the encoding mapping in the coordinate's attributes
        # Convert dict to string for NetCDF serialization
        ds_converted[dim_name].attrs['encoding'] = str(encoding_map)
        ds_converted[dim_name].attrs['original_dtype'] = str(ds[dim_name].dtype)
        ds_converted[dim_name].attrs['description'] = f'Integer-encoded {dim_name} dimension (0-{len(encoding_map)-1})'
        
        print(f"Converted to integers with encoding stored in attributes")
    return ds_converted


def verify_conversion(original_ds, converted_ds, string_dims):
    """Verify that the conversion was successful."""
    print("\nVerifying conversion results...")
    
    for dim_name in string_dims:
        if dim_name not in original_ds.coords:
            continue
            
        print(f"\nDimension: {dim_name}")
        
        # Check that encoding exists
        if 'encoding' not in converted_ds[dim_name].attrs:
            print(f"  ERROR: No encoding found in attributes")
            continue
            
        # Get encoding string and evaluate it back to dict
        encoding_str = converted_ds[dim_name].attrs['encoding']
        try:
            encoding_map = ast.literal_eval(encoding_str)
        except Exception as e:
            print(f"  ERROR: Could not parse encoding string: {e}")
            continue
        
        # Check that dimensions match
        orig_size = original_ds.sizes[dim_name]
        conv_size = converted_ds.sizes[dim_name]
        
        if orig_size != conv_size:
            print(f"  ERROR: Size mismatch - original: {orig_size}, converted: {conv_size}")
            continue
            
        # Check that all original values can be recovered
        original_values = [str(val) for val in original_ds[dim_name].values]
        converted_indices = converted_ds[dim_name].values
        recovered_values = [encoding_map[int(idx)] for idx in converted_indices]

        # Check model dimension separately since we modified capitalization
        # convert the recovered values back to lowercase for comparison
        if dim_name == 'model':
            recovered_values = [
                next((orig for orig in original_values if orig.lower() == rec.lower()), rec)
                for rec in recovered_values
            ]

        if original_values == recovered_values:
            print(f"    Conversion successful - all values recoverable")
            print(f"    Original: {original_values}")
            print(f"    Indices:  {list(converted_indices)}")
            print(f"    Encoding: {encoding_map}")
        else:
            print(f"    ERROR: Values not recoverable")
            print(f"    Original:  {original_values}")
            print(f"    Recovered: {recovered_values}")

def main():
    """Main conversion function."""
    args = parse_arguments()
    
    print("Starting conversion process\n")
    
    # Validate input file
    input_file = Path(args.input_file)
    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)
        
    output_file = Path(args.output_file)
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Variables to convert: All variables to float32")
    print(f"String dimensions to convert: {args.string_dims}")
    print()
    
    # Open input dataset
    print("Opening input dataset...")
    try:
        ds = xr.open_dataset(input_file)
        print(f"Dataset dimensions: {ds.dims}")
        print(f"Dataset coordinates: {list(ds.coords)}")

        # Show current variable info
        print("Data variables:")
        for var_name in ds.data_vars:
            print(f"  {var_name}: {ds[var_name].dtype}")
        print()
        
        # Show current coordinate info
        print("Current coordinate info:")
        for dim_name in args.string_dims:
            if dim_name in ds.coords:
                coord = ds[dim_name]
                print(f"  {dim_name}: {coord.values} (dtype: {coord.dtype})")
        print()
        
    except Exception as e:
        print(f"ERROR opening input file: {e}")
        sys.exit(1)

    # Converting variable data types to float32
    print("Converting variable data types to float32...")
    try:
        for var in ds.data_vars:
            ds = convert_variable_dtype(ds, var, dtype=np.float32)
    except Exception as e:
        print(f"ERROR during variable data type conversion: {e}")
        ds.close()
        sys.exit(1)
    
    # Convert string dimensions
    print("\nConverting string dimensions to integers...")
    try:
        ds_converted = convert_string_dimensions(ds, args.string_dims)
    except Exception as e:
        print(f"ERROR during conversion: {e}")
        ds.close()
        sys.exit(1)
    
    # Verify conversion
    verify_conversion(ds, ds_converted, args.string_dims)
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save converted dataset
    print(f"\nSaving converted dataset to: {output_file}")
    try:
        # Save with compression
        encoding = {}
        for var_name in ds_converted.data_vars:
            encoding[var_name] = {
                'zlib': True, 
                'complevel': 4,
                'shuffle': True
            }
        
        ds_converted.to_netcdf(output_file, format='NETCDF4', encoding=encoding)
        print("Converted dataset saved successfully")
        
        # Show final file info
        file_size = output_file.stat().st_size / 1e9
        print(f"Output file size: {file_size:.2f} GB")
        
    except Exception as e:
        print(f"ERROR saving converted dataset: {e}")
        ds.close()
        ds_converted.close()
        sys.exit(1)
    
    # Verification - try to read the saved file
    print("\nVerifying saved file...")
    try:
        test_ds = xr.open_dataset(output_file)
        print(f"Saved file can be opened successfully")
        print(f"Dimensions: {test_ds.dims}")
        
        # Check encoding attributes
        print("\nEncoding attributes in saved file:")
        for dim_name in args.string_dims:
            if dim_name in test_ds.coords:
                if 'encoding' in test_ds[dim_name].attrs:
                    encoding_str = test_ds[dim_name].attrs['encoding']
                    print(f"  {dim_name}: {encoding_str}")
                else:
                    print(f"  {dim_name}: No encoding attribute found")
        
        test_ds.close()
        
    except Exception as e:
        print(f"ERROR verifying saved file: {e}")
    
    # Clean up
    ds.close()
    ds_converted.close()
    
    print(f"\nConversion completed successfully!")
    print(f"Rasdaman-ready file: {output_file}")


if __name__ == "__main__":
    main()
