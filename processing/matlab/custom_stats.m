function stats = custom_stats(discharge, yr, mo, dy, da_mi2)
% Compute the 12 custom seasonal hydrological statistics not in MHIT.
%
% Python equivalent concept: this is like a regular Python function that
% accepts arrays (think numpy 1-D arrays) and returns a struct (think a
% Python dict or dataclass).
%
% Inputs:
%   discharge  - Nx1 double, daily streamflow (cfs)
%   yr         - Nx1 double, year
%   mo         - Nx1 double, month (1-12)
%   dy         - Nx1 double, day of month
%   da_mi2     - scalar drainage area (square miles); NaN if unavailable
%
% Returns struct with fields:
%   lf1      - Low-flow days: median days/yr with flow below 0.1 cfs/mi²
%   spr_dur3 - Spring high-flow magnitude: median of annual max 3-day mean (Apr-Jun)
%   spr_dur7 - Spring high-flow magnitude: median of annual max 7-day mean (Apr-Jun)
%   sum_dur3 - Summer low-flow magnitude: median of annual min 3-day mean (Jul-Sep)
%   sum_dur7 - Summer low-flow magnitude: median of annual min 7-day mean (Jul-Sep)
%   spr_freq - Spring event frequency: median count/yr of high-flow events (Apr-Jun)
%   sum_freq - Summer event frequency: median count/yr of low-flow events (Jul-Sep)
%   spr_mag  - Spring peak magnitude normalized by drainage area (cfs/mi²)
%   sum_cv   - Summer flow variability: median coefficient of variation (%) in Jul-Sep
%   sum_mag  - Summer low magnitude normalized by drainage area (cfs/mi²)
%   spr_ord  - Spring timing: median Julian day of annual spring peak
%   sum_ord  - Summer timing: median Julian day of annual summer minimum

    % -----------------------------------------------------------------------
    % Initialize all outputs to NaN.
    % In MATLAB a "struct" is like a Python dict: stats.lf1 is equivalent to
    % stats["lf1"]. Setting everything to NaN upfront means any stat that
    % can't be computed (e.g. drainage area is missing) is returned as NaN
    % rather than causing an error or returning nothing.
    % -----------------------------------------------------------------------
    stats.lf1      = NaN;
    stats.spr_dur3 = NaN;
    stats.spr_dur7 = NaN;
    stats.sum_dur3 = NaN;
    stats.sum_dur7 = NaN;
    stats.spr_freq = NaN;
    stats.sum_freq = NaN;
    stats.spr_mag  = NaN;
    stats.sum_cv   = NaN;
    stats.sum_mag  = NaN;
    stats.spr_ord  = NaN;
    stats.sum_ord  = NaN;

    % -----------------------------------------------------------------------
    % Force all input arrays to be column vectors.
    % In Python: arr.flatten() or arr.reshape(-1)
    % The (:) syntax reshapes any array (row, column, or multi-dimensional)
    % into a single column. This prevents shape-mismatch errors later when
    % we do element-wise comparisons between arrays.
    % -----------------------------------------------------------------------
    discharge = discharge(:);
    yr        = yr(:);
    mo        = mo(:);
    dy        = dy(:);

    % -----------------------------------------------------------------------
    % Get the list of unique calendar years and how many there are.
    % In Python: years = np.unique(yr); nyrs = len(years)
    % -----------------------------------------------------------------------
    years = unique(yr);
    nyrs  = numel(years);  % numel = number of elements, like len()

    % =======================================================================
    % STAT 1: LF1 — Low-flow days per year
    % Requires drainage area to normalize flow into runoff depth (cfs/mi²).
    % Counts how many days per year the flow drops below 0.1 cfs/mi², then
    % takes the median across all years.
    % =======================================================================

    % ~isnan() means "is NOT NaN" — equivalent to ~np.isnan() in Python.
    % This block only runs if drainage area was provided.
    if ~isnan(da_mi2) && da_mi2 > 0
        threshold = 0.1 * da_mi2;  % convert 0.1 cfs/mi² to absolute cfs for this gage

        % zeros(nyrs, 1) creates a column array of zeros, length nyrs.
        % Python equivalent: np.zeros(nyrs)
        days_below = zeros(nyrs, 1);

        for i = 1:nyrs  % loop from 1 to nyrs inclusive (MATLAB is 1-indexed)
            % Boolean mask: true for every row belonging to this year.
            % Python equivalent: mask = (yr == years[i])
            % Note: years(i) uses parentheses — MATLAB uses () for both
            % function calls AND array indexing (unlike Python's []).
            mask = yr == years(i);

            % sum(..., 'omitnan') counts true values while ignoring NaN days.
            % Python equivalent: np.sum(discharge[mask] < threshold) ignoring NaN
            days_below(i) = sum(discharge(mask) < threshold, 'omitnan');
        end

        % nanmedian ignores NaN values when computing the median.
        % Python equivalent: np.nanmedian(days_below)
        stats.lf1 = nanmedian(days_below);
    end

    % =======================================================================
    % STATS 2-5: SPR_DUR3, SPR_DUR7, SUM_DUR3, SUM_DUR7
    % Moving-average (rolling mean) based duration/magnitude statistics.
    %
    % Spring (Apr-Jun): we want the PEAK of a smoothed flow signal.
    %   - spr_dur3: median across years of (max 3-day rolling mean in Apr-Jun)
    %   - spr_dur7: same but 7-day rolling window
    %
    % Summer (Jul-Sep): we want the TROUGH of a smoothed flow signal.
    %   - sum_dur3: median across years of (min 3-day rolling mean in Jul-Sep)
    %   - sum_dur7: same but 7-day rolling window
    % =======================================================================

    % NaN(nyrs, 1) creates a column array of NaN values, length nyrs.
    % Python equivalent: np.full(nyrs, np.nan)
    spr_max3 = NaN(nyrs, 1);
    spr_max7 = NaN(nyrs, 1);
    sum_min3 = NaN(nyrs, 1);
    sum_min7 = NaN(nyrs, 1);

    for i = 1:nyrs
        % Compound boolean mask: year matches AND month is in Apr-Jun.
        % Python equivalent: mask = (yr == years[i]) & (mo >= 4) & (mo <= 6)
        spr_mask = yr == years(i) & mo >= 4 & mo <= 6;
        q_spr = discharge(spr_mask);

        % Remove NaN values from the spring subset before computing rolling mean.
        % Python equivalent: q_spr = q_spr[~np.isnan(q_spr)]
        q_spr = q_spr(~isnan(q_spr));

        % Guard: need at least as many data points as the window size.
        % movmean(x, k) computes a centered k-day rolling mean.
        % Python equivalent: pd.Series(q_spr).rolling(k, center=True).mean()
        if numel(q_spr) >= 3
            spr_max3(i) = max(movmean(q_spr, 3));  % peak of 3-day rolling mean
        end
        if numel(q_spr) >= 7
            spr_max7(i) = max(movmean(q_spr, 7));  % peak of 7-day rolling mean
        end

        % Same logic for summer (Jul-Sep), but we take the MINIMUM to capture
        % the low-flow trough.
        sum_mask = yr == years(i) & mo >= 7 & mo <= 9;
        q_sum = discharge(sum_mask);
        q_sum = q_sum(~isnan(q_sum));

        if numel(q_sum) >= 3
            sum_min3(i) = min(movmean(q_sum, 3));  % trough of 3-day rolling mean
        end
        if numel(q_sum) >= 7
            sum_min7(i) = min(movmean(q_sum, 7));  % trough of 7-day rolling mean
        end
    end

    % Summarize across years by taking the median (ignoring years with NaN).
    stats.spr_dur3 = nanmedian(spr_max3);
    stats.spr_dur7 = nanmedian(spr_max7);
    stats.sum_dur3 = nanmedian(sum_min3);
    stats.sum_dur7 = nanmedian(sum_min7);

    % =======================================================================
    % Compute record-wide percentile thresholds for frequency stats below.
    % These thresholds are fixed across all years, not recalculated per year.
    % =======================================================================

    % Remove all NaN values from the full discharge record.
    % Python equivalent: q_clean = discharge[~np.isnan(discharge)]
    q_clean = discharge(~isnan(discharge));

    % If fewer than 2 valid observations exist, we can't compute percentiles.
    % 'return' in MATLAB exits the function early — like Python's return.
    % Stats that haven't been filled yet will stay as NaN (set at the top).
    if numel(q_clean) < 2
        return
    end

    % prctile(x, p) returns the p-th percentile of x.
    % Python equivalent: np.percentile(q_clean, 10) and np.percentile(q_clean, 90)
    p10 = prctile(q_clean, 10);  % 10th percentile of all daily flows
    p90 = prctile(q_clean, 90);  % 90th percentile of all daily flows

    % =======================================================================
    % STAT 6: SPR_FREQ — Spring high-flow event frequency
    % Counts the number of discrete "events" per year where spring (Apr-Jun)
    % flow rises above the record-wide 10th percentile, then takes the median.
    % =======================================================================
    spr_ev = NaN(nyrs, 1);
    for i = 1:nyrs
        mask = yr == years(i) & mo >= 4 & mo <= 6;
        q = discharge(mask);
        if isempty(q), continue; end  % skip year if no spring data at all

        % Create a boolean array: 1 where flow is above threshold, 0 elsewhere.
        above = q > p10;

        % Treat NaN days as "not above threshold" so they don't create
        % spurious event boundaries.
        above(isnan(q)) = false;

        % -----------------------------------------------------------------
        % Event counting trick using diff():
        % diff([0; above; 0]) computes the element-wise difference of the
        % array with a 0 prepended and appended.
        %
        % Python equivalent: np.diff(np.concatenate([[0], above, [0]]))
        %
        % A value of +1 in the diff means the signal just went from 0→1
        % (start of an event). A value of -1 means 1→0 (end of event).
        % Counting the +1s counts the number of distinct events.
        %
        % Example: above = [0,0,1,1,1,0,1,1,0]
        %   padded: [0,0,0,1,1,1,0,1,1,0,0]
        %   diff:   [0,0,1,0,0,-1,1,0,-1,0]
        %   sum(diff==1) = 2  →  two separate high-flow events
        % -----------------------------------------------------------------
        trans = diff([0; above; 0]);
        spr_ev(i) = sum(trans == 1);  % count rising edges = number of events
    end
    stats.spr_freq = nanmedian(spr_ev);

    % =======================================================================
    % STAT 7: SUM_FREQ — Summer low-flow event frequency
    % Same edge-detection logic as SPR_FREQ but for summer (Jul-Sep) and
    % flow dropping BELOW the 90th percentile.
    % =======================================================================
    sum_ev = NaN(nyrs, 1);
    for i = 1:nyrs
        mask = yr == years(i) & mo >= 7 & mo <= 9;
        q = discharge(mask);
        if isempty(q), continue; end

        below = q < p90;
        below(isnan(q)) = false;

        trans = diff([0; below; 0]);  % same rising-edge trick as above
        sum_ev(i) = sum(trans == 1);
    end
    stats.sum_freq = nanmedian(sum_ev);

    % =======================================================================
    % STATS 8 & 10: SPR_MAG and SUM_MAG — Drainage-area-normalized magnitude
    % The raw peak (spring) or trough (summer) flow divided by drainage area,
    % giving units of cfs/mi². This makes gages comparable across basin sizes.
    % =======================================================================
    if ~isnan(da_mi2) && da_mi2 > 0
        spr_max_vals = NaN(nyrs, 1);
        sum_min_vals = NaN(nyrs, 1);

        for i = 1:nyrs
            spr_mask = yr == years(i) & mo >= 4 & mo <= 6;
            q_spr = discharge(spr_mask);
            if ~isempty(q_spr)
                % nanmax ignores NaN — Python equivalent: np.nanmax(q_spr)
                spr_max_vals(i) = nanmax(q_spr);
            end

            sum_mask = yr == years(i) & mo >= 7 & mo <= 9;
            q_sum = discharge(sum_mask);
            if ~isempty(q_sum)
                sum_min_vals(i) = nanmin(q_sum);
            end
        end

        % Divide entire array by scalar da_mi2 (element-wise), then median.
        % Python equivalent: np.nanmedian(spr_max_vals / da_mi2)
        stats.spr_mag = nanmedian(spr_max_vals / da_mi2);
        stats.sum_mag = nanmedian(sum_min_vals / da_mi2);
    end

    % =======================================================================
    % STAT 9: SUM_CV — Summer coefficient of variation
    % CV = (standard deviation / mean) × 100, expressed as a percentage.
    % High CV means summer flows are erratic year to year; low CV means
    % stable baseflow. Computed per year, then median taken across years.
    % =======================================================================
    sum_cv_vals = NaN(nyrs, 1);
    for i = 1:nyrs
        mask = yr == years(i) & mo >= 7 & mo <= 9;
        q = discharge(mask);
        q = q(~isnan(q));  % drop NaNs before std/mean

        % Need at least 2 points for std, and non-zero mean to avoid divide-by-zero.
        if numel(q) > 1 && mean(q) ~= 0
            % std() = standard deviation; mean() = arithmetic mean.
            % Python equivalent: np.std(q, ddof=1) / np.mean(q) * 100
            % Note: MATLAB std() uses ddof=1 (sample std) by default.
            sum_cv_vals(i) = std(q) / mean(q) * 100;
        end
    end
    stats.sum_cv = nanmedian(sum_cv_vals);

    % =======================================================================
    % STATS 11 & 12: SPR_ORD and SUM_ORD — Timing statistics
    % Julian day (day-of-year, 1–365) of the spring peak and summer minimum.
    % Median Julian day tells you when in the year these events typically occur.
    %
    % Julian day is computed manually from month + day-of-month because the
    % input data doesn't include a pre-computed day-of-year column.
    % =======================================================================

    % Cumulative days before the start of each month (non-leap-year).
    % days_per_month(m) is the number of days in month m.
    % cum_days(m) is the Julian day of the FIRST day of month m, minus 1.
    % So Julian day = cum_days(month) + day_of_month.
    %
    % Python equivalent:
    %   days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    %   cum_days = [0] + list(np.cumsum(days_per_month[:11]))
    %
    % Example: May 15 → cum_days(5) + 15 = 120 + 15 = 135
    days_per_month = [31 28 31 30 31 30 31 31 30 31 30 31];
    cum_days = [0, cumsum(days_per_month(1:11))];  % 1×12, one offset per month

    % -------------------------------------------------------------------
    % STAT 11: SPR_ORD — Julian day of spring (Apr-Jun) daily flow peak
    % Uses calendar years (Jan-Dec). Finds the day with the highest flow
    % in each year's Apr-Jun window, records its Julian day, then takes
    % the median across years.
    % -------------------------------------------------------------------
    spr_jday = NaN(nyrs, 1);
    for i = 1:nyrs
        mask = yr == years(i) & mo >= 4 & mo <= 6;
        if ~any(mask), continue; end  % ~any(mask): skip if no rows match

        q = discharge(mask);
        d = dy(mask);  % day-of-month values for this window
        m = mo(mask);  % month values for this window

        % max() returns both the value and the INDEX of the maximum.
        % Python equivalent: idx = np.nanargmax(q); qmax = q[idx]
        [qmax, idx] = max(q);

        if ~isnan(qmax)
            % cum_days(m(idx)) is the number of days before the peak's month.
            % Adding d(idx) gives the Julian day of the peak.
            spr_jday(i) = cum_days(m(idx)) + d(idx);
        end
    end
    stats.spr_ord = nanmedian(spr_jday);

    % -------------------------------------------------------------------
    % STAT 12: SUM_ORD — Julian day of summer (Jul-Sep) daily flow minimum
    % Uses WATER YEARS rather than calendar years. A water year runs Oct 1
    % through Sep 30; water year Y covers Oct (Y-1) through Sep Y.
    %
    % Water year assignment:
    %   water_yr = yr - (mo <= 9)
    %   For months Jan-Sep: mo <= 9 is true (=1), so water_yr = yr - 1,
    %     meaning those months belong to the water year that started the
    %     previous October.
    %   For months Oct-Dec: mo <= 9 is false (=0), so water_yr = yr,
    %     meaning those months start a new water year.
    %
    % Since we only look at Jul-Sep (which are always mo <= 9), every
    % summer window belongs to water_yr = yr - 1. Using water years keeps
    % the Jul-Sep window paired correctly with the preceding Oct-Jun period
    % (consistent with standard hydrological practice).
    % -------------------------------------------------------------------
    water_yr = yr - (mo <= 9);  % reassign each day to its water year
    wyrs = unique(water_yr);
    sum_jday = NaN(numel(wyrs), 1);

    for i = 1:numel(wyrs)
        mask = water_yr == wyrs(i) & mo >= 7 & mo <= 9;
        if ~any(mask), continue; end

        q = discharge(mask);
        d = dy(mask);
        m = mo(mask);

        % min() returns value and index of minimum — same pattern as max() above.
        % Python equivalent: idx = np.nanargmin(q); qmin = q[idx]
        [qmin, idx] = min(q);

        if ~isnan(qmin)
            sum_jday(i) = cum_days(m(idx)) + d(idx);
        end
    end
    stats.sum_ord = nanmedian(sum_jday);
end
