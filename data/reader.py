import fitdecode, datetime
import pandas as pd

# lists of all data fields in the 'record' and 'session' data messages of the binary .fit files
data_fields = ['timestamp', 'position_lat', 'position_long', 'altitude', 'heart_rate', 'cadence',
                'distance', 'speed', 'power', 'compressed_speed_distance', 'grade', 'resistance',
                'time_from_course', 'cycle_length', 'temperature', 'speed_1s', 'cycles', 'total_cycles',
                'compressed_accumulated_power', 'accumulated_power', 'left_right_balance', 'gps_accuracy',
                'vertical_speed', 'calories', 'vertical_oscillation', 'stance_time_percent', 'stance_time',
                'activity_type', 'left_torque_effectiveness', 'right_torque_effectiveness', 'left_pedal_smoothness',
                'right_pedal_smoothness', 'combined_pedal_smoothness', 'time128', 'stroke_type', 'zone',
                'ball_speed', 'cadence256', 'fractional_cadence', 'total_hemoglobin_conc', 'total_hemoglobin_conc_min',
                'total_hemoglobin_conc_max', 'saturated_hemoglobin_percent', 'saturated_hemoglobin_percent_min',
                'saturated_hemoglobin_percent_max', 'device_index', 'left_pco', 'right_pco', 'left_power_phase',
                'left_power_phase_peak', 'right_power_phase', 'right_power_phase_peak', 'enhanced_speed',
                'enhanced_altitude', 'battery_soc', 'motor_power', 'vertical_ratio', 'stance_time_balance',
                'step_length', 'absolute_pressure', 'depth', 'next_stop_depth', 'next_stop_time', 'time_to_surface',
                'ndl_time', 'cns_load', 'n2_load', 'grit', 'flow', 'ebike_travel_range', 'ebike_battery_level',
                'ebike_assist_mode', 'ebike_assist_level_percent']

session_fields = ['message_index', 'timestamp', 'event', 'event_type', 'start_time', 'start_position_lat',
                  'start_position_long', 'sport', 'sub_sport', 'total_elapsed_time', 'total_timer_time',
                  'total_distance', 'total_cycles', 'total_strides', 'total_calories', 'total_fat_calories',
                  'avg_speed', 'max_speed', 'avg_heart_rate', 'max_heart_rate', 'avg_cadence', 'avg_running_cadence',
                  'max_cadence', 'max_running_cadence', 'avg_power', 'max_power', 'total_ascent', 'total_descent',
                  'total_training_effect', 'first_lap_index', 'num_laps', 'event_group', 'trigger', 'nec_lat',
                  'nec_long', 'swc_lat', 'swc_long', 'normalized_power', 'training_stress_score', 'intensity_factor',
                  'left_right_balance', 'avg_stroke_count', 'avg_stroke_distance', 'swim_stroke', 'pool_length',
                  'threshold_power', 'pool_length_unit', 'num_active_lengths', 'total_work', 'avg_altitude',
                  'max_altitude', 'gps_accuracy', 'avg_grade', 'avg_pos_grade', 'avg_neg_grade', 'max_pos_grade',
                  'max_neg_grade', 'avg_temperature', 'max_temperature', 'total_moving_time', 'avg_pos_vertical_speed',
                  'avg_neg_vertical_speed', 'max_pos_vertical_speed', 'max_neg_vertical_speed', 'min_heart_rate',
                  'time_in_hr_zone', 'time_in_speed_zone', 'time_in_cadence_zone', 'time_in_power_zone',
                  'avg_lap_time', 'best_lap_index', 'min_altitude', 'player_score', 'opponent_score', 
                  'opponent_name', 'stroke_count', 'zone_count', 'max_ball_speed', 'avg_ball_speed', 
                  'avg_vertical_oscillation', 'avg_stance_time_percent', 'avg_stance_time', 'avg_fractional_cadence',
                  'max_fractional_cadence', 'total_fractional_cycles', 'avg_total_hemoglobin_conc',
                  'min_total_hemoglobin_conc', 'max_total_hemoglobin_conc', 'avg_saturated_hemoglobin_percent',
                  'min_saturated_hemoglobin_percent', 'max_saturated_hemoglobin_percent', 'avg_left_torque_effectiveness',
                  'avg_right_torque_effectiveness', 'avg_left_pedal_smoothness', 'avg_right_pedal_smoothness', 
                  'avg_combined_pedal_smoothness', 'sport_index', 'time_standing', 'stand_count', 'avg_left_pco',
                  'avg_right_pco', 'avg_left_power_phase', 'avg_left_power_phase_peak', 'avg_right_power_phase',
                  'avg_right_power_phase_peak', 'avg_power_position', 'max_power_position', 'avg_cadence_position',
                  'max_cadence_position', 'enhanced_avg_speed', 'enhanced_max_speed', 'enhanced_avg_altitude',
                  'enhanced_min_altitude', 'enhanced_max_altitude', 'avg_lev_motor_power', 'max_lev_motor_power',
                  'lev_battery_consumption', 'avg_vertical_ratio', 'avg_stance_time_balance', 'avg_step_length',
                  'total_anaerobic_training_effect', 'avg_vam', 'total_grit', 'total_flow', 'jump_count', 'avg_grit',
                  'avg_flow']

# function to read in the data from the .fit file to a pandas data frame
def retrieve_data(file_path, log_file):
    dat = []
    session = []
    try:
        with fitdecode.FitReader(file_path, processor=fitdecode.StandardUnitsDataProcessor()) as fit:
            for frame in fit:
                r = {}
                s = {}
                if isinstance(frame, fitdecode.FitDataMessage):
                    if frame.name == 'record':
                        for name in data_fields:
                            if frame.has_field(name):
                                r[name] = frame.get_value(name)
                        dat.append(r)
                    if frame.name == 'session':
                        for name in session_fields:
                            if frame.has_field(name):
                                s[name] = frame.get_value(name)
                        session.append(s)
        df = pd.DataFrame(dat)
        sf = pd.DataFrame(session)

        with open(log_file, 'a+') as log:
            log.write('\nThe .fit file was read in...') 
        return df, sf

    except Exception as e:
        with open(log_file, 'a+') as log:
            log.write(f'\nSomething went wrong while trying to read in the .fit file. Exception raised: {e}') 

# function to adjust timestamps and writing the moving time in different formats (mainly for plotting)
def calculate(df, sf):
    if 'timestamp' in df:
        df['timestamp'] = df['timestamp'].dt.tz_localize(None)
    if 'timestamp' in sf.columns:
        sf['timestamp'] = sf['timestamp'].dt.tz_localize(None)
    if 'start_time' in sf.columns:
        sf['start_time'] = sf['start_time'].dt.tz_localize(None)
    # if 'power' in df.columns:
    #     NP = (df['power'].rolling(30).mean**4).mean()**(1/4)
    #     return NP
    df['moving_time_seconds'] = (df.timestamp - df.at[0, 'timestamp']).fillna(pd.Timedelta(seconds=0)).astype('timedelta64[s]')
    df['moving_time_minutes'] = df.moving_time_seconds / 60
    df['moving_time_hours'] = df.moving_time_seconds / 3600
    df['moving_time'] = pd.to_datetime(df.moving_time_seconds, unit='s').dt.time