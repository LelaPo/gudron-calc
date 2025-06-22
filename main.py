import os
from colorama import Fore, Style, init

# Инициализация colorama для поддержки цветов в консоли
init(autoreset=True)

# --- Функции для загрузки данных из файлов ---

def load_plant_data(filename="min_sheck_plants.txt"):
    """Загружает данные о растениях (минимальная стоимость, минимальный вес) из файла."""
    plant_data = {}
    if not os.path.exists(filename):
        print(f"{Fore.RED}Ошибка: Файл '{filename}' не найден. Создайте его в формате 'Название: МинСтоимость / МинВес'.{Style.RESET_ALL}")
        return plant_data
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    value_weight_str = parts[1].strip()
                    value_weight_parts = value_weight_str.split('/', 1)
                    if len(value_weight_parts) == 2:
                        try:
                            min_value = float(value_weight_parts[0].strip())
                            min_weight = float(value_weight_parts[1].strip())
                            plant_data[name.lower()] = {'min_value': min_value, 'min_weight': min_weight}
                        except ValueError:
                            print(f"{Fore.YELLOW}Предупреждение: Некорректные числовые данные в строке '{line.strip()}' в файле '{filename}'. Пропускаем.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Предупреждение: Некорректный формат стоимости/веса в строке '{line.strip()}' в файле '{filename}'. Ожидается 'МинСтоимость / МинВес'.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Предупреждение: Некорректный формат строки '{line.strip()}' в файле '{filename}'. Ожидается 'Название: МинСтоимость / МинВес'.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Произошла ошибка при чтении файла '{filename}': {e}{Style.RESET_ALL}")
    return plant_data

def load_mutation_data(filename="mutations.txt"):
    """Загружает данные о мутациях (множитель) из файла."""
    mutation_data = {}
    if not os.path.exists(filename):
        print(f"{Fore.RED}Ошибка: Файл '{filename}' не найден. Создайте его в формате 'Название: Множитель'.{Style.RESET_ALL}")
        return mutation_data
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    try:
                        multiplier = float(parts[1].strip())
                        mutation_data[name.lower()] = multiplier
                    except ValueError:
                        print(f"{Fore.YELLOW}Предупреждение: Некорректный числовой множитель в строке '{line.strip()}' в файле '{filename}'. Пропускаем.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Предупреждение: Некорректный формат строки '{line.strip()}' в файле '{filename}'. Ожидается 'Название: Множитель'.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Произошла ошибка при чтении файла '{filename}': {e}{Style.RESET_ALL}")
    return mutation_data

# --- Вспомогательные функции для поиска по сокращению ---

def find_match(query, data_dict, data_type="растения"):
    """
    Ищет совпадение в словаре по частичному вводу.
    Возвращает список полных названий совпадений.
    """
    query_lower = query.lower()
    matches = [key for key in data_dict.keys() if query_lower in key]
    return matches

def select_item_from_matches(matches, data_dict, item_type="растение"):
    """
    Позволяет пользователю выбрать элемент из списка совпадений.
    Возвращает выбранное название в нижнем регистре или None.
    """
    if not matches:
        print(f"{Fore.RED}Совпадений не найдено.{Style.RESET_ALL}")
        return None
    elif len(matches) == 1:
        chosen_item = matches[0]
        confirm = input(f"{Fore.CYAN}Выбрано {item_type.capitalize()}: {chosen_item.capitalize()}. Оставить? (y/n, по умолчанию 'y'): {Style.RESET_ALL}").lower()
        if confirm == 'n':
            return None
        else:
            return chosen_item
    else:
        print(f"{Fore.YELLOW}Найдено несколько {item_type}ий:{Style.RESET_ALL}")
        for i, match in enumerate(matches):
            print(f"{i+1}. {match.capitalize()}")
        while True:
            try:
                choice = input(f"{Fore.CYAN}Введите номер {item_type}а или 0 для повторного ввода: {Style.RESET_ALL}")
                choice_int = int(choice)
                if 0 < choice_int <= len(matches):
                    return matches[choice_int - 1]
                elif choice_int == 0:
                    return None
                else:
                    print(f"{Fore.RED}Некорректный номер. Пожалуйста, введите номер из списка.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Некорректный ввод. Пожалуйста, введите число.{Style.RESET_ALL}")

# --- Основная логика калькулятора ---

def calculate_plant_value():
    plant_data = load_plant_data()
    mutation_bonuses = load_mutation_data()

    if not plant_data:
        print(f"{Fore.RED}Не удалось загрузить данные о растениях. Калькулятор не может работать.{Style.RESET_ALL}")
        return
    if not mutation_bonuses:
        print(f"{Fore.RED}Не удалось загрузить данные о мутациях. Калькулятор не может работать.{Style.RESET_ALL}")
        return

    # ASCII заголовок - вставь сюда свою надпись "gudron"
    # Я немного скорректировал отступы для ASCII-арта, чтобы он выглядел ровнее
    ascii_header = f"""{Fore.GREEN}

                  .___                                            .__          
   ____  __ __  __| ________  ____   ____             ____ _____  |  |   ____  
  / ___\|  |  \/ __ |\_  __ \/  _ \ /    \   ______ _/ ___\\__  \ |  | _/ ___\ 
 / /_/  |  |  / /_/ | |  | \(  <_> |   |  \ /_____/ \  \___ / __ \|  |_\  \___ 
 \___  /|____/\____ | |__|   \____/|___|  /          \___  (____  |____/\___  >
/_____/            \/                   \/               \/     \/          \/ 
             
{Style.RESET_ALL}"""
    print(ascii_header)
    print(f"{Fore.YELLOW}--- Калькулятор стоимости растений Grow A Garden ---{Style.RESET_ALL}")

    while True:
        plant_name_input = None
        plant_info = None

        while plant_info is None:
            query = input(f"\n{Fore.CYAN}Введите название растения (или 'выход' для завершения): {Style.RESET_ALL}").lower()
            if query == 'выход':
                return

            matches = find_match(query, plant_data, "растения")
            selected_plant_name = select_item_from_matches(matches, plant_data, "растение")

            if selected_plant_name:
                plant_name_input = selected_plant_name
                plant_info = plant_data[plant_name_input]
            else:
                print(f"{Fore.RED}Пожалуйста, попробуйте ввести название растения снова.{Style.RESET_ALL}")

        min_value = plant_info['min_value']
        min_weight = plant_info['min_weight']

        while True:
            try:
                mass_input = float(input(f"{Fore.CYAN}Введите вес растения '{plant_name_input.capitalize()}' (кг): {Style.RESET_ALL}"))
                if mass_input <= 0:
                    print(f"{Fore.RED}Вес должен быть положительным числом.{Style.RESET_ALL}")
                else:
                    break
            except ValueError:
                print(f"{Fore.RED}Некорректный ввод. Пожалуйста, введите числовое значение для веса.{Style.RESET_ALL}")

        growth_mutations_options = {'nona': 1, 'gold': 20, 'rainbow': 50}
        growth_mutation_multiplier = 1 # По умолчанию Nona
        growth_mut_display_name = 'Nona' # Для вывода

        environmental_mutations_input = input(f"{Fore.CYAN}Введите мутации (роста и/или окружающей среды) через запятую (например, shock, gold): {Style.RESET_ALL}").lower()
        
        raw_selected_mutations = [m.strip() for m in environmental_mutations_input.split(',') if m.strip()]
        selected_environmental_mutations = [] 
        
        temp_growth_mut_found = False
        for mut in raw_selected_mutations:
            if mut in growth_mutations_options:
                if temp_growth_mut_found:
                    print(f"{Fore.YELLOW}Предупреждение: Обнаружено более одной мутации роста (Gold/Rainbow) в вашем вводе. Будет использована последняя введенная.{Style.RESET_ALL}")
                growth_mutation_multiplier = growth_mutations_options[mut]
                growth_mut_display_name = mut.capitalize()
                temp_growth_mut_found = True
            else:
                selected_environmental_mutations.append(mut)

        invalid_combinations = False
        group_gold_rainbow = {'gold', 'rainbow'}
        group_chilled_wet_frozen = {'chilled', 'wet', 'frozen'}
        group_cooked_burnt = {'cooked', 'burnt'}

        growth_muts_in_env_input = set(raw_selected_mutations).intersection(group_gold_rainbow)
        if len(growth_muts_in_env_input) > 1:
             print(f"{Fore.YELLOW}Предупреждение: Обнаружено более одной мутации роста (Gold/Rainbow) в вашем вводе. Убедитесь, что вы выбрали правильную.{Style.RESET_ALL}")

        if len(set(selected_environmental_mutations).intersection(group_chilled_wet_frozen)) > 1:
            print(f"{Fore.RED}Ошибка: Можно выбрать только одну мутацию из Chilled, Wet или Frozen.{Style.RESET_ALL}")
            invalid_combinations = True
        if len(set(selected_environmental_mutations).intersection(group_cooked_burnt)) > 1:
            print(f"{Fore.RED}Ошибка: Можно выбрать только одну мутацию из Cooked или Burnt.{Style.RESET_ALL}")
            invalid_combinations = True
        if 'dawnbound' in selected_environmental_mutations and plant_name_input != 'sunflower':
            print(f"{Fore.RED}Ошибка: Мутация Dawnbound может быть применена только к Sunflower.{Style.RESET_ALL}")
            invalid_combinations = True

        if invalid_combinations:
            print(f"{Fore.RED}Пожалуйста, исправьте выбор мутаций и попробуйте снова.{Style.RESET_ALL}")
            continue

        sum_of_environmental_stack_bonuses = 0
        processed_environmental_mutations = []
        for mut_query in selected_environmental_mutations:
            matches = find_match(mut_query, mutation_bonuses, "мутации")
            
            if len(matches) == 1:
                chosen_mut_name = matches[0]
                processed_environmental_mutations.append(chosen_mut_name)
                sum_of_environmental_stack_bonuses += (mutation_bonuses[chosen_mut_name] - 1)
            elif len(matches) > 1:
                print(f"{Fore.YELLOW}Предупреждение: Несколько совпадений для '{mut_query}': {', '.join([m.capitalize() for m in matches])}. Мутация будет проигнорирована, если не может быть однозначно определена.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Предупреждение: Мутация '{mut_query}' не найдена в списке известных мутаций и будет проигнорирована.{Style.RESET_ALL}")

        total_multiplier = growth_mutation_multiplier * (1 + sum_of_environmental_stack_bonuses)

        final_value = 0
        if mass_input <= min_weight:
            final_value = min_value * total_multiplier
            print(f"\n{Fore.BLUE}Вес ({mass_input} кг) <= Минимального веса ({min_weight} кг). Используется формула: Min Value * Total Multiplier{Style.RESET_ALL}")
        else:
            if min_weight == 0:
                 print(f"{Fore.RED}Ошибка: Минимальный вес растения не может быть равен 0 для расчета по формуле с весом^2.{Style.RESET_ALL}")
                 continue
            k_constant = min_value / (min_weight ** 2)
            final_value = k_constant * (mass_input ** 2) * total_multiplier
            print(f"\n{Fore.BLUE}Вес ({mass_input} кг) > Минимального веса ({min_weight} кг). Используется формула: k * Weight^2 * Total Multiplier{Style.RESET_ALL}")
            print(f"{Fore.BLUE}Расчетное k для этого растения: {k_constant:,.2f}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}--- Результаты расчета ---{Style.RESET_ALL}")
        print(f"  {Fore.WHITE}Растение:{Style.RESET_ALL} {plant_name_input.capitalize()}")
        print(f"  {Fore.WHITE}Вес:{Style.RESET_ALL} {mass_input} кг")
        print(f"  {Fore.WHITE}Мутация роста:{Style.RESET_ALL} {growth_mut_display_name} (x{growth_mutation_multiplier})")
        print(f"  {Fore.WHITE}Выбранные мутации окружающей среды:{Style.RESET_ALL} {', '.join([m.capitalize() for m in processed_environmental_mutations]) if processed_environmental_mutations else 'Нет'}")
        print(f"  {Fore.WHITE}Сумма Stack Bonuses:{Style.RESET_ALL} {sum_of_environmental_stack_bonuses:,.2f}")
        print(f"  {Fore.WHITE}Общий множитель (Total Multiplier):{Style.RESET_ALL} {total_multiplier:,.2f}")

        # Выделение итоговой стоимости
        final_price_label = "Итоговая стоимость: "
        final_price_value_str = f"{final_value:,.2f} Шекелей"
        full_price_line = final_price_label + final_price_value_str
        
        # Adjusting the padding for the box.
        # Adding 4 for the corners and inner spaces (e.g., "|  text  |")
        box_width = len(full_price_line) + 4 

        print(f"\n{Fore.YELLOW}{Style.BRIGHT}+{'-' * box_width}+{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}|  {final_price_label}{Fore.MAGENTA}{Style.BRIGHT}{final_price_value_str}  |{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}+{'-' * box_width}+{Style.RESET_ALL}")

# --- Запуск калькулятора ---
if __name__ == "__main__":
    calculate_plant_value()