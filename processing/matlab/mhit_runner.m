% mhit_runner.m
% MATLAB batch script for computing MHIT + custom hydrological statistics.
%
% Called from SLURM via:
%   matlab -batch "run('/path/to/mhit_runner.m')"
%
% Required environment variables (set by the SLURM job script):
%   MHIT_CSV_DIR  - directory containing per-stream discharge CSVs + drainageArea.csv
%   MHIT_OUT_DIR  - directory to write results.csv
%   MHIT_MFILES   - path to MHIT/MFiles directory (addpath target)
%   MHIT_NCORES   - number of parallel workers (defaults to 4)

csv_dir  = getenv('MHIT_CSV_DIR');
out_dir  = getenv('MHIT_OUT_DIR');
mfiles   = getenv('MHIT_MFILES');
ncores_s = getenv('MHIT_NCORES');

if isempty(csv_dir) || isempty(out_dir) || isempty(mfiles)
    error('Required env vars MHIT_CSV_DIR, MHIT_OUT_DIR, MHIT_MFILES must be set.');
end

ncores = 4;
if ~isempty(ncores_s)
    ncores = str2double(ncores_s);
end

addpath(mfiles);

% Ensure output dir exists
if ~exist(out_dir, 'dir')
    mkdir(out_dir);
end

% Find all discharge CSVs (excluding drainageArea.csv)
csv_files = dir(fullfile(csv_dir, '*.csv'));
is_da = strcmpi({csv_files.name}, 'drainageArea.csv');
csv_files = csv_files(~is_da);
n_files = numel(csv_files);

if n_files == 0
    error('No discharge CSV files found in %s', csv_dir);
end
fprintf('Processing %d files with %d parallel workers...\n', n_files, ncores);

% Read drainage area lookup by column position to avoid MATLAB renaming
% mixed-case CSV headers (e.g. 'fileName' -> 'FileName') on import.
da_raw       = readtable(fullfile(csv_dir, 'drainageArea.csv'));
da_filenames = da_raw{:, 1};   % cell array of stream basenames
da_areas     = da_raw{:, 2};   % double array of drainage areas (mi2)

% Column names for the output table
% MHIT indices: 40 stats
% Custom stats: 12 stats
% Total: 52 stats
stat_names = { ...
    'ma3','ma4', ...
    'ma12','ma13','ma14','ma15','ma16','ma17','ma18','ma19','ma20','ma21','ma22','ma23', ...
    'mh14','mh20','ml17', ...
    'dh1','dh2','dh3','dh4','dh5','dh15', ...
    'dl1','dl2','dl3','dl4','dl5','dl16', ...
    'fh1','fh5','fh6','fh7','fl1','fl3', ...
    'ra1','ra3','ra8', ...
    'th1','tl1', ...
    'lf1','spr_dur3','spr_dur7','sum_dur3','sum_dur7', ...
    'spr_freq','sum_freq','spr_mag','sum_cv','sum_mag', ...
    'spr_ord','sum_ord' ...
};
n_stats = numel(stat_names);

% Pre-allocate result matrix (rows=files, cols=stats).
% da_filenames and da_areas broadcast as simple array/cell to parfor workers.
result_matrix = NaN(n_files, n_stats);
file_names    = cell(n_files, 1);

% Start parallel pool
try
    pool = gcp('nocreate');
    if isempty(pool)
        parpool(ncores);
    elseif pool.NumWorkers ~= ncores
        delete(pool);
        parpool(ncores);
    end
catch e
    warning('Could not start parallel pool (%s); running serially.', e.message);
end

parfor i = 1:n_files
    fname = csv_files(i).name;
    fbase = fname(1:end-4);
    file_names{i} = fbase;
    row = NaN(1, n_stats);

    try
        data = readtable(fullfile(csv_dir, fname));

        % Require columns: year month day discharge
        if ~all(ismember({'year','month','day','discharge'}, data.Properties.VariableNames))
            continue
        end

        % Get drainage area for this file
        da_idx = strcmpi(da_filenames, fbase);
        if any(da_idx)
            da_mi2 = da_areas(find(da_idx, 1));
        else
            da_mi2 = NaN;
        end

        q  = double(data.discharge);
        yr = double(data.year);
        mo = double(data.month);
        dy = double(data.day);

        % Clip to complete water years (Oct-Sep).
        % Partial years at the era boundaries cause cellfun errors inside MHIT
        % because some per-year computations return [] instead of a scalar.
        water_yr = yr - (mo <= 9);
        wy_unique = unique(water_yr);
        months_per_wy = arrayfun(@(wy) numel(unique(mo(water_yr == wy))), wy_unique);
        complete_wys = wy_unique(months_per_wy >= 12);
        keep = ismember(water_yr, complete_wys);
        q  = q(keep);
        yr = yr(keep);
        mo = mo(keep);
        dy = dy(keep);

        % Skip if less than 2 years of non-NaN data remain after clipping
        q_valid = q(~isnan(q));
        if numel(q_valid) < 730
            continue
        end

        % --- MHIT indices ---
        [idx_all, ~] = mhit_getAllIndices(q, yr, mo, dy, da_mi2);

        row(1)  = safe_get(idx_all.MA, 3);   % ma3
        row(2)  = safe_get(idx_all.MA, 4);   % ma4
        row(3)  = safe_get(idx_all.MA, 12);  % ma12
        row(4)  = safe_get(idx_all.MA, 13);  % ma13
        row(5)  = safe_get(idx_all.MA, 14);  % ma14
        row(6)  = safe_get(idx_all.MA, 15);  % ma15
        row(7)  = safe_get(idx_all.MA, 16);  % ma16
        row(8)  = safe_get(idx_all.MA, 17);  % ma17
        row(9)  = safe_get(idx_all.MA, 18);  % ma18
        row(10) = safe_get(idx_all.MA, 19);  % ma19
        row(11) = safe_get(idx_all.MA, 20);  % ma20
        row(12) = safe_get(idx_all.MA, 21);  % ma21
        row(13) = safe_get(idx_all.MA, 22);  % ma22
        row(14) = safe_get(idx_all.MA, 23);  % ma23
        row(15) = safe_get(idx_all.MH, 14);  % mh14
        row(16) = safe_get(idx_all.MH, 20);  % mh20
        row(17) = safe_get(idx_all.ML, 17);  % ml17
        row(18) = safe_get(idx_all.DH, 1);   % dh1
        row(19) = safe_get(idx_all.DH, 2);   % dh2
        row(20) = safe_get(idx_all.DH, 3);   % dh3
        row(21) = safe_get(idx_all.DH, 4);   % dh4
        row(22) = safe_get(idx_all.DH, 5);   % dh5
        row(23) = safe_get(idx_all.DH, 15);  % dh15
        row(24) = safe_get(idx_all.DL, 1);   % dl1
        row(25) = safe_get(idx_all.DL, 2);   % dl2
        row(26) = safe_get(idx_all.DL, 3);   % dl3
        row(27) = safe_get(idx_all.DL, 4);   % dl4
        row(28) = safe_get(idx_all.DL, 5);   % dl5
        row(29) = safe_get(idx_all.DL, 16);  % dl16
        row(30) = safe_get(idx_all.FH, 1);   % fh1
        row(31) = safe_get(idx_all.FH, 5);   % fh5
        row(32) = safe_get(idx_all.FH, 6);   % fh6
        row(33) = safe_get(idx_all.FH, 7);   % fh7
        row(34) = safe_get(idx_all.FL, 1);   % fl1
        row(35) = safe_get(idx_all.FL, 3);   % fl3
        row(36) = safe_get(idx_all.RA, 1);   % ra1
        row(37) = safe_get(idx_all.RA, 3);   % ra3
        row(38) = safe_get(idx_all.RA, 8);   % ra8
        row(39) = safe_get(idx_all.TH, 1);   % th1
        row(40) = safe_get(idx_all.TL, 1);   % tl1

        % --- Custom seasonal stats ---
        cs = custom_stats(q, yr, mo, dy, da_mi2);
        row(41) = cs.lf1;
        row(42) = cs.spr_dur3;
        row(43) = cs.spr_dur7;
        row(44) = cs.sum_dur3;
        row(45) = cs.sum_dur7;
        row(46) = cs.spr_freq;
        row(47) = cs.sum_freq;
        row(48) = cs.spr_mag;
        row(49) = cs.sum_cv;
        row(50) = cs.sum_mag;
        row(51) = cs.spr_ord;
        row(52) = cs.sum_ord;

    catch e
        fprintf('  WARNING: error on %s: %s\n', fbase, getReport(e, 'extended', 'hyperlinks', 'off'));
    end

    result_matrix(i, :) = row;
end

% Assemble and write output table
T = array2table(result_matrix, 'VariableNames', stat_names);
T.fileName = file_names;
% Move fileName to first column
T = [T(:, end), T(:, 1:end-1)];

out_csv = fullfile(out_dir, 'results.csv');
writetable(T, out_csv);
fprintf('Wrote %s  (%d rows x %d stat columns)\n', out_csv, n_files, n_stats);


function val = safe_get(arr, idx)
% Return arr(idx) or NaN if idx is out of bounds or value is non-finite.
    if numel(arr) >= idx
        val = arr(idx);
        if ~isfinite(val)
            val = NaN;
        end
    else
        val = NaN;
    end
end
